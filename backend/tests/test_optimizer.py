import unittest
from backend.models.container import Container
from backend.models.yard import Yard
from backend.models.yard_config import YardConfig
from backend.optimizer.optimizer import Optimizer

class TestOptimizer(unittest.TestCase):
    def setUp(self):
        config = YardConfig(
            length=5, width=5, height=3,
            energy_consumption_rate=0.1,
            carbon_emission_factor=0.5,
            max_weight_per_stack=5000,
            crane_speed=2,
            crane_energy_consumption=5
        )
        self.yard = Yard(config)
        self.optimizer = Optimizer(self.yard)
        self.container = Container(
            id="CONT001",
            weight=1000,
            destination="Port A",
            arrival_date="2023-05-01",
            departure_date="2023-05-10"
        )

    def test_optimize_placement(self):
        position = self.optimizer.optimize_placement(self.container)
        self.assertIsNotNone(position)
        self.assertTrue(self.yard.add_container(self.container, position))

    def test_calculate_metrics(self):
        self.yard.add_container(self.container, (0, 0, 0))
        metrics = self.optimizer.calculate_metrics()
        self.assertIn("total_containers", metrics)
        self.assertIn("total_moves", metrics)
        self.assertIn("optimized_moves", metrics)

if __name__ == '__main__':
    unittest.main()
