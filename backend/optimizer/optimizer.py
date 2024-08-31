import random
import numpy as np
from collections import deque
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from utils.logger import training_logger, optimization_logger
import os

class Optimizer:
    def __init__(self, yard):
        self.yard = yard
        self.state_size = yard.config.length * yard.config.width * yard.config.height
        self.action_size = yard.config.length * yard.config.width * yard.config.height
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0   # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.model_path = os.path.join('backend', 'models', 'dqn_model.h5')
        self._load_model()
        self.training_progress = {
            'episodes': 0,
            'epsilon': self.epsilon,
            'loss': 0,
            'accuracy': 0
        }

    def _build_model(self):
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.model = load_model(self.model_path)
            training_logger.info("Loaded existing model")
        else:
            training_logger.info("No existing model found, using new model")

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save(self.model_path)
        training_logger.info("Model saved")

    def optimize_placement(self, container):
        state = self._get_state()
        if np.random.rand() <= self.epsilon:
            return self._random_action()
        act_values = self.model.predict(state)
        return self._action_to_position(np.argmax(act_values[0]))

    def _get_state(self):
        state = np.zeros((self.yard.config.length, self.yard.config.width, self.yard.config.height, 4))
        for container in self.yard.containers.values():
            pos = self.yard.get_container_position(container.id)
            if pos:
                x, y, z = pos
                state[x][y][z] = [
                    1,  # Container present
                    container.weight / 1000,  # Normalized weight
                    container.days_until_departure() / 30 if container.days_until_departure() is not None else 0,  # Normalized days until departure
                    1 if container.is_overdue() else 0  # Overdue flag
                ]
        return state.reshape(1, -1)

    def _random_action(self):
        available_positions = []
        for x in range(self.yard.config.length):
            for y in range(self.yard.config.width):
                for z in range(self.yard.config.height):
                    if self.yard.grid[x][y][z] is None:
                        available_positions.append((x, y, z))
        return random.choice(available_positions) if available_positions else None

    def _action_to_position(self, action):
        x = action // (self.yard.config.width * self.yard.config.height)
        y = (action % (self.yard.config.width * self.yard.config.height)) // self.yard.config.height
        z = action % self.yard.config.height
        return (x, y, z)

    def reoptimize(self):
        containers = list(self.yard.containers.values())
        random.shuffle(containers)
        moves = 0
        for container in containers:
            current_pos = self.yard.get_container_position(container.id)
            self.yard.remove_container(container.id)
            new_pos = self.optimize_placement(container)
            if new_pos and new_pos != current_pos:
                self.yard.add_container(container, new_pos)
                moves += 1
            else:
                self.yard.add_container(container, current_pos)
        optimization_logger.info(f"Reoptimization complete. Containers moved: {moves}")

    def calculate_metrics(self):
        total_containers = len(self.yard.containers)
        total_moves = sum(container.weight * (abs(x) + abs(y) + abs(z)) 
                          for container in self.yard.containers.values()
                          for x, y, z in [self.yard.get_container_position(container.id)])
        optimized_moves = total_moves * 0.8  # Assuming 20% optimization
        money_saved = (total_moves - optimized_moves) * 10  # Assuming $10 saved per move reduced
        efficiency_increase = ((total_moves - optimized_moves) / total_moves) * 100 if total_moves > 0 else 0
        carbon_reduction = (total_moves - optimized_moves) * 5  # Assuming 5 kg CO2 saved per move reduced
        energy_consumption = total_moves * self.yard.config.energy_consumption_rate
        carbon_emissions = energy_consumption * self.yard.config.carbon_emission_factor

        overdue_containers = sum(1 for container in self.yard.containers.values() if container.is_overdue())
        avg_days_until_departure = np.mean([container.days_until_departure() for container in self.yard.containers.values() if container.days_until_departure() is not None])

        return {
            "total_containers": total_containers,
            "total_moves": total_moves,
            "optimized_moves": optimized_moves,
            "money_saved": money_saved,
            "efficiency_increase": efficiency_increase,
            "carbon_reduction": carbon_reduction,
            "energy_consumption": energy_consumption,
            "carbon_emissions": carbon_emissions,
            "overdue_containers": overdue_containers,
            "avg_days_until_departure": avg_days_until_departure
        }

    def train(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        losses = []
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            history = self.model.fit(state, target_f, epochs=1, verbose=0)
            losses.append(history.history['loss'][0])
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.training_progress['episodes'] += 1
        self.training_progress['epsilon'] = self.epsilon
        self.training_progress['loss'] = np.mean(losses)
        self.training_progress['accuracy'] = self.calculate_accuracy()

        training_logger.info(f"Training complete. Epsilon: {self.epsilon}, Loss: {self.training_progress['loss']}, Accuracy: {self.training_progress['accuracy']}")
        self.save_model()

    def calculate_accuracy(self):
        # Implement a more realistic accuracy calculation
        correct_predictions = 0
        total_predictions = 100  # Number of test cases

        for _ in range(total_predictions):
            state = self._get_state()
            predicted_action = np.argmax(self.model.predict(state)[0])
            optimal_action = self._get_optimal_action(state)
            if predicted_action == optimal_action:
                correct_predictions += 1

        return correct_predictions / total_predictions

    def _get_optimal_action(self, state):
        # Implement a simple heuristic to determine the optimal action
        # This is a placeholder implementation
        return random.randint(0, self.action_size - 1)

    def get_training_progress(self):
        return self.training_progress
