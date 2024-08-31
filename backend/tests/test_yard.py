import unittest
from backend.models.container import Container
from backend.models.yard import Yard
from backend.models.yard_config import YardConfig
from backend.optimizer.optimizer import Optimizer

class TestYard(unittest.TestCase):
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
        self.container = Container(
            id="CONT001",
            weight=1000,
            destination="Port A",
            arrival_date="2023-05-01",
            departure_date="2023-05-10"
        )

    def test_add_container(self):
        result = self.yard.add_container(self.container, (0, 0, 0))
        self.assertTrue(result)
        self.assertEqual(self.yard.containers[self.container.id], self.container)

    def test_remove_container(self):
        self.yard.add_container(self.container, (0, 0, 0))
        result = self.yard.remove_container(self.container.id)
        self.assertTrue(result)
        self.assertNotIn(self.container.id, self.yard.containers)

    def test_move_container(self):
        self.yard.add_container(self.container, (0, 0, 0))
        result = self.yard.move_container(self.container.id, (1, 1, 1))
        self.assertTrue(result)
        self.assertEqual(self.yard.get_container_position(self.container.id), (1, 1, 1))

if __name__ == '__main__':
    unittest.main()
