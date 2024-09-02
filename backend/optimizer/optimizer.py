import random
import numpy as np
from collections import deque
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from backend.utils.logger import training_logger, optimization_logger
import os

class Optimizer:
    def __init__(self, yard):
        self.yard = yard
        self.state_size = yard.config.length * yard.config.width * yard.config.height * 4  # 4 features per position
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
        model.add(Dense(64, input_shape=(self.state_size,), activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
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
                    container.weight / self.yard.config.max_weight_per_stack,  # Normalized weight
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
        containers.sort(key=lambda c: (c.is_overdue(), -c.days_until_departure() if c.days_until_departure() is not None else 0))
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
        return moves

    def calculate_metrics(self):
        total_containers = len(self.yard.containers)
        total_weight = sum(container.weight for container in self.yard.containers.values())
        overdue_containers = sum(1 for container in self.yard.containers.values() if container.is_overdue())
        avg_days_until_departure = np.mean([container.days_until_departure() for container in self.yard.containers.values() if container.days_until_departure() is not None])
        
        total_moves = sum(abs(x) + abs(y) + abs(z) 
                          for container in self.yard.containers.values()
                          for x, y, z in [self.yard.get_container_position(container.id)])
        
        energy_consumption = total_moves * self.yard.config.crane_energy_consumption
        carbon_emissions = energy_consumption * self.yard.config.carbon_emission_factor
        
        yard_utilization = len(self.yard.containers) / (self.yard.config.length * self.yard.config.width * self.yard.config.height)
        
        stack_heights = [max([z for x, y, z in [self.yard.get_container_position(c.id)] if x == i and y == j] + [0])
                         for i in range(self.yard.config.length) for j in range(self.yard.config.width)]
        avg_stack_height = np.mean(stack_heights)
        max_stack_height = max(stack_heights)

        return {
            "total_containers": total_containers,
            "total_weight": total_weight,
            "overdue_containers": overdue_containers,
            "avg_days_until_departure": avg_days_until_departure,
            "total_moves": total_moves,
            "energy_consumption": energy_consumption,
            "carbon_emissions": carbon_emissions,
            "yard_utilization": yard_utilization,
            "avg_stack_height": avg_stack_height,
            "max_stack_height": max_stack_height
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
        correct_predictions = 0
        total_predictions = 100

        for _ in range(total_predictions):
            state = self._get_state()
            predicted_action = np.argmax(self.model.predict(state)[0])
            optimal_action = self._get_optimal_action(state)
            if predicted_action == optimal_action:
                correct_predictions += 1

        return correct_predictions / total_predictions

    def _get_optimal_action(self, state):
        # Implement a heuristic to determine the optimal action
        state_reshaped = state.reshape((self.yard.config.length, self.yard.config.width, self.yard.config.height, 4))
        best_score = float('-inf')
        best_action = None

        for x in range(self.yard.config.length):
            for y in range(self.yard.config.width):
                for z in range(self.yard.config.height):
                    if state_reshaped[x][y][z][0] == 0:  # Empty position
                        score = self._calculate_position_score(x, y, z, state_reshaped)
                        if score > best_score:
                            best_score = score
                            best_action = x * self.yard.config.width * self.yard.config.height + y * self.yard.config.height + z

        return best_action if best_action is not None else random.randint(0, self.action_size - 1)

    def _calculate_position_score(self, x, y, z, state):
        # Calculate a score for placing a container at the given position
        # Higher score means better placement
        score = 0
        
        # Prefer lower positions
        score -= z * 10
        
        # Prefer positions with containers below
        if z > 0 and state[x][y][z-1][0] == 1:
            score += 5
        
        # Prefer positions away from overdue containers
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    nx, ny, nz = x + dx, y + dy, z + dz
                    if 0 <= nx < self.yard.config.length and 0 <= ny < self.yard.config.width and 0 <= nz < self.yard.config.height:
                        if state[nx][ny][nz][3] == 1:  # Overdue container
                            score -= 3
        
        return score

    def get_training_progress(self):
        return self.training_progress
