import os
import json
import re
import csv
from collections import namedtuple
from typing import Generator, List, Dict, Union, Tuple

VERBOSE=False

MeasureSection = namedtuple('MeasureSection', ['measure', 'section'])
MeasureResultId = namedtuple('MeasureResultId', ['Measure', 'PatientGUID', 'GroupId'])

header = ["measure_name", "guid", "population", "count"]

allowed_display_names = {
    "Initial Population",
    "Denominator",
    "Denominator Exclusion",
    "Denominator Exclusions",
    "Denominator Exception",
    "Denominator Exceptions",
    "Numerator",
    "Numerator Exclusion",
    "Numerator Exclusions",
    "Measure Observation",
    "Measure Observations",
    "Measure Population",
    "Measure Population Observation",
    "Measure Population Observations",
    "Measure Population Exclusion",
    "Measure Population Exclusions"
}

patient_pattern = re.compile(r'Patient\s*=\s*Patient\(id=(?P<id>[a-f0-9\-]+)\)')
expression_pattern = re.compile(rf'^(?P<expression>(?:{"|".join(list(allowed_display_names))})(?:\s*\d*))\s*=\s*(?P<value>.*)')
section_pattern = re.compile(r'\n\s*\n')   # Split sections by two line breaks instead of hyphens

def log(message: str):
    if VERBOSE:
        print(message)

def find_all_groups_by_expression(measure_criteria: Dict[str, Dict[str, str]], expression: str) -> Dict[str, str]:
    return {group: criteria_map[expression] for group, criteria_map in measure_criteria.items() if expression in criteria_map}

def extract_measure_criteria(measure_data: Dict) -> Dict[str, Dict[str, str]]:
    """Extract Measure Criteria 

    Args:
        measure_data (Dict): measure results data from a CQL results txt file

    Returns:
        Dict[str, Dict[str, str]]: Measure Criteria as Dict[<GROUP ID>, Dict[<EXPRESSION>, <POPULATION>]]
    """
    measure_criteria = {}
    for group in measure_data.get('group', []):
        criteria_map = measure_criteria.setdefault(group['id'], {})
        for pop in group.get('population', []):
            expression = pop.get('criteria', {}).get('expression', '')
            population = pop.get('code', {}).get('coding', [{}])[0].get('display', '')
            # Index by measure_name, group_id, and expression
            criteria_map[expression] = population
    return measure_criteria

def load_measure_criteria(measure_resource_dir: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Load Measure Criteria from all files in the specified directory

    Args:
        measure_resource_dir (str): path to directory with measure resource files

    Returns:
        Dict[str, Dict[str, Dict[str, str]]]: All Measure Criteria as Dict[<MEASURE NAME>, Dict[<GROUP ID>, Dict[<EXPRESSION>, <POPULATION>]]]
    """
    measure_criteria_map = {}
    for measure_file in os.listdir(measure_resource_dir):
        if measure_file.endswith('.json'):
            measure_path = os.path.join(measure_resource_dir, measure_file)
            measure_name = os.path.splitext(measure_file)[0]
            with open(measure_path, 'r') as f:
                measure_data = json.load(f)
                measure_criteria = extract_measure_criteria(measure_data)
                measure_criteria_map[measure_name] = measure_criteria
    return measure_criteria_map

def parse_count(result_value: str) -> Union[int, str]:
    result_value = result_value.strip()
    if result_value.lower() == "true":
        return 1
    elif result_value.lower() == "false":
        return 0
    elif result_value.lower() == "null":
        return 0
    elif result_value.startswith("[") and result_value.endswith("]"):
        items = [item.strip() for item in result_value[1:-1].split(",") if item.strip()]
        return len(items)
    else:
        return result_value  # fallback, could be a number or string

def validate_numerator(populations: Dict[str, str]):
    # scoring validation based on https://build.fhir.org/ig/HL7/cqf-measures/measure-conformance.html#proportion-measure-scoring
    denom = populations.get('Denominator', 0)
    denex = populations.get('Denominator Exclusion', 0)
    numer = populations.get('Numerator', 0)
    numex = populations.get('Numerator Exclusion', 0)
    
    if not denom and denex:
        denex = 0

    if numer and (denom and denex) or not denom:
        numer = 0

    if not numer and numex:
        numex = 0

    # save updated scoring back to population, but only if the value already existed in the population
    if 'Numerator'in populations:
        populations['Numerator'] = numer
    if 'Denominator Exclusion'in populations:
        populations['Denominator Exclusion'] = denex
    if 'Numerator Exclusion'in populations:
        populations['Numerator Exclusion'] = numex

def load_measure_sections(dir_path: str) -> Generator['MeasureSection', None, None]:
    """Load Measure Sections from VS Code CQL Extension result files
    
    Args:
        dir_path (str): path to directory with VSCode CQL Extension result files
    
    Yields:
        Generator['MeasureSection', None, None]: A generator object that yields MeasureSections
    """
    for file_name in os.listdir(dir_path):
        # Skip hidden/system files like .DS_Store
        if file_name.startswith('.') or not file_name.endswith('.txt'):
            continue
        log(f' {file_name}')
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            measure_name = os.path.splitext(file_name)[0]
            with open(file_path, "r") as f:
                content = f.read()
            sections = section_pattern.split(content)
            for section in sections:
                yield MeasureSection(measure_name, section)

def create_empty_populations(measure_name:str, patient_guid: str, measure_criteria: Dict[str, Dict[str, str]]) -> Dict[MeasureResultId, Dict[str, str]]:
    return {
        MeasureResultId(measure_name, patient_guid, group): {population: 0 for population in expression_population_map.values()}
        for group, expression_population_map in measure_criteria.items()
    }

def capture_results(measure_sections: Generator['MeasureSection', None, None], all_measure_criteria: Dict[str, Dict[str, Dict[str, str]]]) -> Dict[MeasureResultId, Dict[str, str]]:
    """Convert measure sections (data from VSCode CQL extension results)

    Args:
        measure_sections (Generator[&#39;MeasureSection&#39;, None, None]): A generator object that yields MeasureSections
        all_measure_criteria (Dict[str, Dict[str, Dict[str, str]]]): All Measure Criteria as Dict[<MEASURE NAME>, Dict[<GROUP ID>, Dict[<EXPRESSION>, <POPULATION>]]]

    Returns:
        Dict[MeasureResultId, Dict[str, str]]: Results that match the allowed_display_names.
    """
    results = {}
    for measure_section in measure_sections:
        measure_name = measure_section.measure
        section_data = measure_section.section
        patient_guid_match = patient_pattern.search(section_data)
        if patient_guid_match:
            patient_guid = patient_guid_match.group('id')
            results.update(create_empty_populations(measure_name, patient_guid, all_measure_criteria[measure_section.measure]))
            for line in section_data.splitlines():
                expression_match = expression_pattern.search(line)
                if expression_match:
                    measure_criteria = all_measure_criteria[measure_name]
                    for group, population in find_all_groups_by_expression(measure_criteria, expression_match.group('expression')).items():
                        results[MeasureResultId(measure_name, patient_guid, group)][population] = parse_count(expression_match.group('value'))
    return results

def convert_results_to_rows(results: Dict[MeasureResultId, Dict[str, str]]) -> List[List[str]]:
    # convert results dict to rows
    # during conversion verify that proper proportional eCQM population criteria rules are followed
    rows = []
    for measure_id, populations in results.items():
        validate_numerator(populations)
        for population, count in populations.items():
            rows.append([measure_id.Measure, measure_id.PatientGUID, f'{measure_id.GroupId}:{population}', count])
    return rows

def save_results(output_file: str, rows: List[List[str]]):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(rows)

if __name__ == '__main__':
    VERBOSE=True
    measure_resource_dir = "./input/resources/measure"
    output_file = "./scripts/comparison/actual_results.csv"
    results_dir = "./input/tests/results"

    log("Loading Measure Criteria")
    all_measure_criteria =  load_measure_criteria(measure_resource_dir)

    log("Loading Measures")
    measure_sections = load_measure_sections(results_dir)

    log("Capturing Results")
    results = capture_results(measure_sections, all_measure_criteria)

    log("Analyzing Results")
    rows = convert_results_to_rows(results)

    log("Saving Results")
    save_results(output_file, rows)
