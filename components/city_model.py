"""A square street grid; distances are kilometres, times are minutes."""
import random


class CityGrid:
    def __init__(self, side_km=4, num_parallel_streets=9, rng=None):
        if side_km <= 0 or num_parallel_streets < 3 or num_parallel_streets % 2 != 1:
            raise ValueError("Use a positive side and an odd street count of at least 3")
        self.side = side_km
        self.num_parallel_streets = int(num_parallel_streets)
        self.rng = rng or random.Random()
        self.dark_store_loc = (0.0, 0.0)
        self.customer_locs = self.generate_locs()
        self.assigned_locs = []

    def generate_locs(self):
        half = self.num_parallel_streets // 2
        step = self.side / (self.num_parallel_streets - 1)
        return [(x * step, y * step) for x in range(-half, half + 1)
                for y in range(-half, half + 1) if x or y]

    def sample_loc(self):
        if not self.customer_locs:
            raise ValueError("No unassigned grid locations remain")
        loc = self.rng.choice(self.customer_locs)
        self.customer_locs.remove(loc)
        self.assigned_locs.append(loc)
        return loc

    @staticmethod
    def route_length(loc1, loc2):
        return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
