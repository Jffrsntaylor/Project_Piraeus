import csv
from ..models.container import Container

def parse_csv(file_path):
    containers = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                container = Container(
                    id=row['id'],
                    weight=float(row['weight']),
                    destination=row['destination'],
                    arrival_date=row['arrival_date'],
                    departure_date=row['departure_date']
                )
                containers.append(container)
            except (ValueError, KeyError) as e:
                print(f"Error parsing row: {row}. Error: {str(e)}")
    return containers
