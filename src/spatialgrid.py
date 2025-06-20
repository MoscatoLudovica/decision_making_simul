from collections import defaultdict

class SpatialGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = defaultdict(list)

    def _cell_coords(self, pos):
        return (int(pos.x // self.cell_size), int(pos.y // self.cell_size))

    def clear(self):
        self.grid.clear()

    def insert(self, agent):
        cell = self._cell_coords(agent.get_position())
        self.grid[cell].append(agent)

    def neighbors(self, agent, radius):
        pos = agent.get_position()
        cell_x, cell_y = self._cell_coords(pos)
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell = (cell_x + dx, cell_y + dy)
                for other in self.grid.get(cell, []):
                    if other is not agent:
                        if (other.get_position() - pos).magnitude() <= radius:
                            neighbors.append(other)
        return neighbors
    
    def close(self):
        del self.grid, self.cell_size
        return