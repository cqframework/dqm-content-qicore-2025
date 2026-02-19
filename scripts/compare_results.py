import os
import csv
import glob
import re
from collections import namedtuple
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, NamedTuple, Set, Tuple, TypedDict

measure_id_pattern = r"(?:CMS|CMSFHIR)(?P<measure_id>\d+)"

MeasureDifference = namedtuple('MeasureDifference', ['measure', 'total_test_cases', 'test_cases_with_differences', 'result_deltas'])
ResultKey = namedtuple('ResultKey', ['measure_name', 'patient_guid', 'group'])
ResultDelta = namedtuple('ResultDelta', ['patient_guid', 'group', 'population', 'expected', 'actual'])
Comparison = namedtuple('Comparison', ['expected', 'actual'])
TestCaseGroupId = namedtuple('TestCaseId', ['patient_guid', 'group'])

# source: https://terminology.hl7.org/CodeSystem-measure-population.html
ValidMeasurePopulationTypes = [
    'Initial Population',
    'Numerator',
    'Numerator Exclusion',
    'Numerator Observations',
    'Denominator',
    'Denominator Exclusion',
    'Denominator-exclusion',
    'Denominator-exception',
    'Denominator Exception',
    'Denominator Observations',
    'Measure Population',
    'Measure Population Exclusion'
]

class MissingPopulation(NamedTuple):
    result_key: ResultKey
    population: List[str]

class Discrepancies(NamedTuple):
    missing_results: List[ResultKey]
    missing_populations: List[MissingPopulation]
    population_differences: Dict[str, List[str]]
    measures_with_discrepancies: Set[str]

@dataclass
class MeasureDiscrepancy:
    all_test_cases: List[str] = field(default_factory=list)
    missing_results: List[ResultKey] = field(default_factory=list)
    missing_populations: List[MissingPopulation] = field(default_factory=list)
    mismatched_test_cases: Dict[TestCaseGroupId, Dict[str, Comparison]] = field(default_factory=dict)

class Results(NamedTuple):
    rows: Dict[str, str]
    groups: Dict[ResultKey, Dict[str, str]]

def capture_results(file: str) -> Results:
    rows = {}
    results = {}
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["measure_name"], row["guid"], row["population"])
            rows[key] = row["count"]

            group_and_population = row["population"].split(':')
            if group_and_population[1] not in ValidMeasurePopulationTypes:
                continue

            result_key = ResultKey(row["measure_name"], row["guid"], group_and_population[0])
            result = results.setdefault(result_key, {})
            result[group_and_population[1]] = row["count"]
    return Results(rows, results)

def generate_output(file: str, expected_rows: Dict, actual_rows: Dict) -> Tuple[int, int]:
    header = ["result", "measure_name", "guid", "population", "expected_result", "actual_result"]
    output = []

    pass_count = 0
    fail_count = 0

    for key, expected_result in expected_rows.items():
        # key fields: [ 'measure_name', 'patient_guid', 'group' ]
        # verify the population
        if key[2].split(':')[1] not in ValidMeasurePopulationTypes:
            # TODO: include 'bad' population in report so user know why population wasn't used in report
            continue

        actual_result = actual_rows.get(key)
        if actual_result is None or str(expected_result) != str(actual_result):
            output.append(["FAIL", key[0], key[1], key[2], expected_result, actual_result if actual_result is not None else "MISSING"])
            fail_count += 1
        else:
            output.append(["PASS", key[0], key[1], key[2], expected_result, actual_result])
            pass_count += 1

    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(output)

    return (pass_count, fail_count)

def create_markdown_table(headers: List[str], data: List[str], custom_separator_row: str=None) -> List[str]:
    table_rows = []

    # header row
    table_rows.append(f'| {" | ".join(headers)} |\n')

    # separator row
    table_rows.append(custom_separator_row if custom_separator_row else f'| {" | ".join(["---"] * len(headers))} |\n')

    # data rows
    for row_data in data:
        table_rows.append("| " + " | ".join(map(str, row_data)) + " |\n")
    table_rows.append('\n\n')
    return table_rows

def sort_measure_names(measure_names: List[str]) -> List[str]:
    measures_with_numbers_in_name = []
    for measure_name in measure_names:
        match = re.match(measure_id_pattern, measure_name)
        if match:
            measures_with_numbers_in_name.append(f'{match.group("measure_id")}---{measure_name}')
    sorted_measures_with_numbers_in_name = [m.split('---')[1] for m in sorted(measures_with_numbers_in_name, key=lambda x: int(x.split('---')[0]))]
    return sorted_measures_with_numbers_in_name + \
        [m for m in sorted([m for m in measure_names if m not in sorted_measures_with_numbers_in_name])]

def sort_populations(populations: List[str]) -> List[str]:
    order = {
        'initial population': 1,
        'denominator': 2,
        'denominator exclusion': 3,
        'denominator exception': 4,
        'numerator': 5,
        'numerator exclusion': 6}
    return sorted(populations, key=lambda x: order[x.lower()] if x.lower() in order else 99)

def cql_file_link(measure_name: str, custom_id: str = None) -> str:
    return f'[ {custom_id} ](../../input/cql/{measure_name}.cql)' if custom_id else f'[ {measure_name} ](../../input/cql/{measure_name}.cql)'

def measure_report_file_link(measure_name: str, patient_guid: str) -> str:
    # path relative to root directory, this is the expected location for running the script
    measure_dir = f'./input/tests/measure/{measure_name}/{patient_guid}/'
    measure_report_file = glob.glob(f'{measure_dir}/MeasureReport*.json')
    if measure_report_file:
        # path relative to this script, need to add parent directories
        return f'[ {patient_guid} ](../../{measure_report_file[0]})'
    else:
        return patient_guid

def test_results_file_link(measure_name: str, custom_id: str = None) -> str:
    return f'[ {custom_id} ](../../input/tests/results/{measure_name}.txt)' if custom_id else f'[ {measure_name} ](../../input/tests/results/{measure_name}.txt)'

def capture_discrepancies_by_measure(expected_results: Dict[ResultKey, Dict[str, str]], actual_results: Dict[ResultKey, Dict[str, str]]) -> Dict[str, MeasureDiscrepancy]:
    def has_discrepancy(discrepancy: MeasureDiscrepancy) -> bool:
        return discrepancy.missing_populations or \
           discrepancy.missing_results or \
           discrepancy.mismatched_test_cases

    discrepancies = {}
    for expected_results_key, expected_populations in expected_results.items():
        measure_discrepancy = discrepancies.setdefault(expected_results_key.measure_name, MeasureDiscrepancy())
        measure_discrepancy.all_test_cases.append(expected_results_key.patient_guid)
        if expected_results_key not in actual_results:
            measure_discrepancy.missing_results.append(expected_results_key)
        else:
            actual_populations = actual_results[expected_results_key]
            # confirm all expected populations exist
            population_delta = list(set(expected_populations.keys()) - set(actual_populations.keys()))
            if population_delta:
                measure_discrepancy.missing_populations.append(MissingPopulation(expected_results_key, population_delta))
            else:
                mismatched_populations = { population: Comparison(expected_populations[population], actual_populations[population])
                     for population in expected_populations.keys() & actual_populations.keys() if expected_populations[population] != actual_populations[population]}
                if mismatched_populations:
                    measure_discrepancy.mismatched_test_cases[TestCaseGroupId(expected_results_key.patient_guid, expected_results_key.group)] = mismatched_populations
    return {measure: discrepancies[measure] for measure in sort_measure_names([k for k,v in discrepancies.items() if has_discrepancy(v)])}

def generate_comparison_report(file: str, expected_results: Dict[ResultKey, Dict[str, str]], actual_results: Dict[ResultKey, Dict[str, str]]):
    discrepancies = capture_discrepancies_by_measure(expected_results, actual_results)

    with open(file, "w", newline="") as f:
        f.write('# Discrepancy Report\n')
        f.writelines(create_markdown_table(
            ['Details', 'Value'],
            [
                ['Generated', datetime.now()],
                ['Total Measures', len(set([result_key.measure_name for result_key in expected_results.keys()]))],
                ['Total Test Cases', len(set([(result_key.measure_name, result_key.patient_guid) for result_key in expected_results.keys()]))],
                ['Measures with Discrepancies', len(discrepancies)]
            ]
        ))
        f.writelines(create_markdown_table(
            ['Discrepancy Summary', 'Measure Count', 'Test Case Count'],
            [
                [
                    'Missing Results', 
                    len(set([measure for measure, discrepancy  in discrepancies.items() if discrepancy.missing_results])),
                    sum([len(discrepancy.missing_results) for discrepancy in discrepancies.values()])
                ],
                [
                    'Missing Populations', 
                    len(set([measure for measure, discrepancy  in discrepancies.items() if discrepancy.missing_populations])),
                    sum([len(discrepancy.missing_populations) for discrepancy in discrepancies.values()])
                ],
                [
                    'Mismatched Test Cases', 
                    len(set([measure for measure, discrepancy  in discrepancies.items() if discrepancy.mismatched_test_cases])),
                    sum([len(discrepancy.mismatched_test_cases.keys()) for discrepancy in discrepancies.values()])
                ]
            ],
            '|---|:---:|:---:|\n'))
        f.write('\n')
        f.write('_Note: Measures can have multiple discrepancies, so the Measures with Discrepancies count may not match the summary counts._\n')

        non_discrepancy_measures = [measure_name for measure_name in sort_measure_names(list(set([k.measure_name for k in expected_results.keys()]))) if measure_name not in discrepancies]
        if non_discrepancy_measures:
            f.write(f'## Measures with No Discrepancies ({len(non_discrepancy_measures)})\n')
            for measure in non_discrepancy_measures:
                f.write(f'- {measure} {cql_file_link(measure,'[cql]')} {test_results_file_link(measure,'[test results]')}\n')

        if discrepancies:
            f.write(f'## Measures with Discrepancies ({len(discrepancies)})\n')
            f.writelines(create_markdown_table(
                ['Measure', 'Total Test Cases', 'Missing Results', 'Missing Populations', 'Mismatched Test Cases'],
                [
                    [
                        f'[{measure}](#{measure.lower()})',
                        len(discrepancy.all_test_cases),
                        len(discrepancy.missing_results),
                        len(discrepancy.missing_populations),
                        f'{len(discrepancy.mismatched_test_cases)/len(discrepancy.all_test_cases)*100:.2f}%   ({len(discrepancy.mismatched_test_cases)})'
                    ] for measure, discrepancy in discrepancies.items()
                ],
                '|---|:---:|:---:|:---:|:---:|\n'))
            f.write('\n')

            for measure, discrepancy in discrepancies.items():
                f.write(f'#### {measure}\n')
                f.write(f'{cql_file_link(measure, '[cql]')} {test_results_file_link(measure, '[test results]')}\n\n')

                if discrepancy.missing_results:
                    f.write(f'Missing Results ({len(discrepancy.missing_results)} of {len(discrepancy.all_test_cases)} test cases)\n')
                    f.writelines(create_markdown_table(
                        ['Test Case', 'Group'],
                        [[
                            measure_report_file_link(missing_id.measure_name, missing_id.patient_guid),
                            missing_id.group
                         ] for missing_id in discrepancy.missing_results]))
            
                if discrepancy.missing_populations:
                    f.write(f'Missing Populations ({len(discrepancy.missing_populations)} of {len(discrepancy.all_test_cases)} test cases)\n')
                    f.writelines(create_markdown_table(
                        ['Test Case', 'Group', 'Population'],
                        [[
                            measure_report_file_link(missing_id.measure_name, missing_id.patient_guid),
                            missing_id.group,
                            ','.join(populations)] for (missing_id, populations) in discrepancy.missing_populations]))
            
                if discrepancy.mismatched_test_cases:
                    f.write(f'Mismatched Test Cases ({len(discrepancy.mismatched_test_cases)} of  of {len(discrepancy.all_test_cases)})\n')
                    f.writelines(create_markdown_table(
                        ['Test Case', 'Group', 'Population', 'Expected', 'Actual'],
                        [[
                            measure_report_file_link(measure, test_group_id.patient_guid),
                            test_group_id.group,
                            '<br>'.join([population for population in sort_populations(populations.keys())]),
                            '<br>'.join([populations[population].expected for population in sort_populations(populations.keys())]),
                            '<br>'.join([populations[population].actual for population in sort_populations(populations.keys())])
                         ] for test_group_id, populations in discrepancy.mismatched_test_cases.items()],
                        '|---|---|---|:---:|:---:|\n'))

def main(expected_file: str, actual_file: str, output_file: str, comparison_report: str):
    expected_results = capture_results(expected_file)
    actual_results = capture_results(actual_file)

    pass_fail_count = generate_output(output_file, expected_results[0], actual_results[0])
    pass_pct = pass_fail_count[0] / (pass_fail_count[0] + pass_fail_count[1]) * 100
    print(f"PASS: {pass_fail_count[0]} ({pass_pct:.2f})%")
    print(f"FAIL: {pass_fail_count[1]} ({(100 - pass_pct):.2f})%")
    
    generate_comparison_report(comparison_report, expected_results[1], actual_results[1])

if __name__ == '__main__':
    expected_file = "./scripts/comparison/expected_results.csv"
    actual_file = "./scripts/comparison/actual_results.csv"
    output_file = "./scripts/comparison/output_results.csv"
    comparison_report = "./scripts/comparison/discrepancy_report.md"

    main(expected_file, actual_file, output_file, comparison_report)
