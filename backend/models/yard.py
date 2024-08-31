class Yard:
    def __init__(self, config):
        self.config = config
        self.containers = {}
        self.grid = [[[None for _ in range(config.height)] for _ in range(config.width)] for _ in range(config.length)]

    def add_container(self, container, position):
        x, y, z = position
        if self.grid[x][y][z] is None and self._check_weight_limit(x, y, z, container.weight):
            self.grid[x][y][z] = container
            self.containers[container.id] = container
            return True
        return False

    def _check_weight_limit(self, x, y, z, container_weight):
        stack_weight = sum(self.grid[x][y][i].weight for i in range(z) if self.grid[x][y][i] is not None)
        return stack_weight + container_weight <= self.config.max_weight_per_stack

    def remove_container(self, container_id):
        if container_id in self.containers:
            container = self.containers[container_id]
            for x in range(self.config.length):
                for y in range(self.config.width):
                    for z in range(self.config.height):
                        if self.grid[x][y][z] == container:
                            self.grid[x][y][z] = None
                            del self.containers[container_id]
                            return True
        return False

    def get_container_position(self, container_id):
        for x in range(self.config.length):
            for y in range(self.config.width):
                for z in range(self.config.height):
                    if self.grid[x][y][z] and self.grid[x][y][z].id == container_id:
                        return (x, y, z)
        return None

    def move_container(self, container_id, new_position):
        container = self.containers.get(container_id)
        if not container:
            return False

        current_position = self.get_container_position(container_id)
        if not current_position:
            return False

        x, y, z = new_position
        if self.grid[x][y][z] is not None:
            return False

        self.grid[current_position[0]][current_position[1]][current_position[2]] = None
        self.grid[x][y][z] = container
        return True

    def calculate_move_time(self, start_pos, end_pos):
        x1, y1, z1 = start_pos
        x2, y2, z2 = end_pos
        distance = abs(x2 - x1) + abs(y2 - y1) + abs(z2 - z1)
        return distance / self.config.crane_speed

    def calculate_move_energy(self, start_pos, end_pos):
        move_time = self.calculate_move_time(start_pos, end_pos)
        return move_time * self.config.crane_energy_consumption
