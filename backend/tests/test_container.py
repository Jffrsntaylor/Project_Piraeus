import unittest
from datetime import datetime, timedelta
from backend.models.container import Container
from backend.models.container import Container
from backend.models.yard import Yard
from backend.models.yard_config import YardConfig
from backend.optimizer.optimizer import Optimizer

class TestContainer(unittest.TestCase):
    def setUp(self):
        self.container = Container(
            id="CONT001",
            weight=1000,
            destination="Port A",
            arrival_date="2023-05-01",
            departure_date="2023-05-10"
        )

    def test_days_until_departure(self):
        self.container.departure_date = datetime.now() + timedelta(days=5)
        self.assertEqual(self.container.days_until_departure(), 5)

    def test_is_overdue(self):
        self.container.departure_date = datetime.now() - timedelta(days=1)
        self.assertTrue(self.container.is_overdue())

    def test_to_dict(self):
        container_dict = self.container.to_dict()
        self.assertEqual(container_dict['id'], "CONT001")
        self.assertEqual(container_dict['weight'], 1000)
        self.assertEqual(container_dict['destination'], "Port A")

if __name__ == '__main__':
    unittest.main()
