from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from .database import Base
from datetime import datetime, timedelta

class Container(Base):
    __tablename__ = "containers"

    id = Column(String, primary_key=True, index=True)
    weight = Column(Float)
    destination = Column(String)
    arrival_date = Column(DateTime)
    departure_date = Column(DateTime)
    content_type = Column(String)
    is_refrigerated = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    last_moved = Column(DateTime)

    def __init__(self, id, weight, destination, arrival_date, departure_date, content_type=None, is_refrigerated=False, priority=0):
        self.id = id
        self.weight = float(weight)
        self.destination = destination
        self.arrival_date = self._parse_date(arrival_date)
        self.departure_date = self._parse_date(departure_date)
        self.content_type = content_type
        self.is_refrigerated = is_refrigerated
        self.priority = priority
        self.last_moved = datetime.now()

    def _parse_date(self, date_string):
        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            return None

    def __repr__(self):
        return f"Container({self.id}, {self.weight}, {self.destination}, {self.content_type})"

    def days_until_departure(self):
        if self.departure_date:
            return max((self.departure_date - datetime.now()).days, 0)
        return None

    def is_overdue(self):
        if self.departure_date:
            return datetime.now() > self.departure_date
        return False

    def time_since_last_move(self):
        return (datetime.now() - self.last_moved).total_seconds() / 3600  # Return hours

    def update_last_moved(self):
        self.last_moved = datetime.now()

    def calculate_storage_cost(self, cost_per_day):
        if self.arrival_date:
            days_in_storage = (datetime.now() - self.arrival_date).days
            return days_in_storage * cost_per_day
        return 0

    def to_dict(self):
        return {
            "id": self.id,
            "weight": self.weight,
            "destination": self.destination,
            "arrival_date": self.arrival_date.strftime("%Y-%m-%d") if self.arrival_date else None,
            "departure_date": self.departure_date.strftime("%Y-%m-%d") if self.departure_date else None,
            "content_type": self.content_type,
            "is_refrigerated": self.is_refrigerated,
            "priority": self.priority,
            "days_until_departure": self.days_until_departure(),
            "is_overdue": self.is_overdue(),
            "time_since_last_move": self.time_since_last_move()
        }
