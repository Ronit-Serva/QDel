"""Shared simulation entry point for the CLI and browser worker."""
from dataclasses import dataclass, asdict
import math
import random
import simpy

from components.city_model import CityGrid
from components.customer import customer_factory
from components.dark_store import DarkStore
from components.platform import Platform
from components.rider import rider_factory


@dataclass
class Config:
    customers: int = 160
    riders: int = 12
    processors: int = 4
    orders_per_hour: int = 60
    speed_kmh: int = 20
    duration: int = 120
    seed: int = 42
    sla: int = 15
    dispatch: str = "fifo"

    def __post_init__(self):
        if self.dispatch not in ("fifo", "shortest_trip"):
            raise ValueError("dispatch must be fifo or shortest_trip")
        bounds = {"customers": (4, 1000), "riders": (1, 60), "processors": (1, 20),
                  "orders_per_hour": (1, 240), "speed_kmh": (5, 50),
                  "duration": (10, 480), "seed": (0, 999999), "sla": (5, 60)}
        for key, (low, high) in bounds.items():
            value = getattr(self, key)
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{key} must be an integer between {low} and {high}")


class Simulation:
    def __init__(self, config=None):
        self.config = config or Config()
        c = self.config
        self.env = simpy.Environment()
        # Separate demand and service RNGs keep arrival streams comparable across staffing scenarios.
        self.demand_rng = random.Random(c.seed)
        self.rng = random.Random(c.seed + 1)
        self.city = CityGrid(4, 9, self.rng)
        self.store = DarkStore(self.env, c.processors)
        riders = rider_factory(self.env, c.riders, self.store)
        self.platform = Platform(self.env, self.city, self.store, riders, self.rng, c.speed_kmh, c.dispatch)
        self.store.platform = self.platform
        self.platform.customers = customer_factory(self.env, c.customers, self.platform)
        self.env.process(self.arrivals())
        self.history = []
        self.next_sample = 1

    def arrivals(self):
        while True:
            yield self.env.timeout(self.demand_rng.expovariate(self.config.orders_per_hour / 60))
            if self.env.now >= self.config.duration:
                return
            # An attempt to order while this customer is waiting does not create a duplicate.
            customer = self.demand_rng.choice(self.platform.customers)
            if customer.state == "idle":
                customer.order()

    def advance(self, minutes=1):
        if isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or not math.isfinite(minutes) or minutes <= 0:
            raise ValueError("Advance must be a positive finite number of minutes")
        target = min(self.config.duration, self.env.now + minutes)
        while self.next_sample <= target:
            self.env.run(until=self.next_sample)
            self.history.append({"time": self.env.now, **self.metrics()})
            self.next_sample += 1
        if target > self.env.now:
            self.env.run(until=target)
        return self.snapshot()

    def metrics(self):
        orders = self.platform.orders
        done = [o for o in orders if o.delivered_at is not None]
        times = sorted(o.delivered_at - o.timestamp for o in done)
        active = [o for o in orders if o.delivered_at is None]
        now = self.env.now
        def utilization(resources):
            busy = sum(r.busy_minutes + (now - r.started_at if r.started_at is not None else 0) for r in resources)
            return 100 * busy / (len(resources) * now) if now else 0
        return {"placed": len(orders), "delivered": len(done), "active": len(active),
                "queued": sum(o.status in ("queued", "ready") for o in orders),
                "avg_delivery": sum(times) / len(times) if times else None,
                "p95_delivery": times[max(0, math.ceil(.95 * len(times)) - 1)] if times else None,
                "on_time": 100 * sum(t <= self.config.sla for t in times) / len(times) if times else None,
                "overdue": sum(now - o.timestamp > self.config.sla for o in active),
                "rider_utilization": utilization(self.platform.riders),
                "packer_utilization": utilization(self.store.processors)}

    def snapshot(self):
        return {"time": self.env.now, "finished": self.env.now >= self.config.duration,
                "config": asdict(self.config), "metrics": self.metrics(),
                "orders": [o.read_order() for o in self.platform.orders],
                "customers": [{"id": c.id, "loc": c.loc, "state": c.state} for c in self.platform.customers],
                "riders": [{"id": r.id, "state": r.state, "loc": r.location(self.env.now),
                            "start": r.start, "destination": r.destination,
                            "order": r.order_key, "deliveries": r.deliveries} for r in self.platform.riders],
                "events": self.platform.events[-40:], "history": self.history}
