from sqlalchemy import Column, Integer, Float, String, DateTime
from .database import Base
from datetime import datetime

class Container(Base):
    __tablename__ = "containers"

    id = Column(String, primary_key=True, index=True)
    weight = Column(Float)
    destination = Column(String)
    arrival_date = Column(DateTime)
    departure_date = Column(DateTime)

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
            return None

    def __repr__(self):
        return f"Container({self.id}, {self.weight}, {self.destination})"

    def days_until_departure(self):
        if self.departure_date:
            return (self.departure_date - datetime.now()).days
        return None

    def is_overdue(self):
        if self.departure_date:
            return datetime.now() > self.departure_date
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "weight": self.weight,
            "destination": self.destination,
            "arrival_date": self.arrival_date.strftime("%Y-%m-%d") if self.arrival_date else None,
            "departure_date": self.departure_date.strftime("%Y-%m-%d") if self.departure_date else None,
            "days_until_departure": self.days_until_departure(),
            "is_overdue": self.is_overdue()
        }
