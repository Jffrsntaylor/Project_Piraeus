from datetime import datetime

class Container:
    def __init__(self, id, weight, destination, arrival_date, departure_date):
        self.id = id
        self.weight = float(weight)
        self.destination = destination
        self.arrival_date = self._parse_date(arrival_date)
        self.departure_date = self._parse_date(departure_date)

    def _parse_date(self, date_string):
        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            # If the date is invalid, return None or raise an exception
            return None

    def __repr__(self):
        return f"Container({self.id}, {self.weight}, {self.destination})"
