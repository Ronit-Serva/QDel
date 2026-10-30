"""Customers have fixed homes and can have one outstanding order."""
import math

from .city_model import CityGrid


class Customer:
    def __init__(self, env, loc, platform, customer_id=None):
        self.env, self.loc, self.platform = env, loc, platform
        self.id = customer_id or f"C{len(platform.customers) + 1:03d}"
        self.type = "regular"
        self.state = "idle"

    def order(self):
        return self.platform.place_order(self, self.env.now)


def customer_factory(env, num_customers, platform):
    if not isinstance(num_customers, int) or num_customers < 1:
        raise ValueError("Customer count must be a positive integer")
    n = max(3, math.ceil(math.sqrt(math.ceil(num_customers / 4) + 1)))
    if n % 2 == 0:
        n += 1
    city = platform.city or CityGrid(4, n, platform.rng)
    locations = city.generate_locs()
    platform.rng.shuffle(locations)
    return [Customer(env, locations[(i // 4) % len(locations)], platform,
                     f"C{i + 1:03d}") for i in range(num_customers)]
