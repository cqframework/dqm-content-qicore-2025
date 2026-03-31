import os
import json
import csv

base_dir = "./input/tests/measure/"
measure_resource_dir = "./input/resources/measure"
output_file = "./scripts/comparison/expected_results.csv"

header = ["measure_name", "guid", "population", "count"]
rows = []

for measure_name in os.listdir(base_dir):
    measure_path = os.path.join(base_dir, measure_name)
    if os.path.isdir(measure_path):
        for root, _, files in os.walk(measure_path):
            for file in files:
                if file.startswith("MeasureReport-") and file.endswith(".json"):
                    guid = os.path.basename(root)
                    file_path = os.path.join(root, file)
                    print("Parsing MeasureReport resource:", file_path)
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        for group in data.get("group", []):
                            if group.get("id").startswith("Group_"):
                                for pop in group.get("population", []):
                                    if pop.get("id") == 'MeasureObservation_1_1_1':
                                        pop_name = 'Denominator Observation'
                                    elif pop.get("id") == 'MeasureObservation_1_2_1':
                                        pop_name = 'Numerator Observation'
                                    else:
                                        pop_name = pop.get("code", {}).get("coding", [{}])[0].get("display", "")
                                    rows.append([
                                        measure_name, 
                                        guid, 
                                        f'{group.get("id")}:{pop_name}', 
                                        pop.get('count', '')])

os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(output_file, "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)
    writer.writerows(rows)