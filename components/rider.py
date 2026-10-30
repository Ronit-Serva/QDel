import simpy


class Rider:
    def __init__(self, env, cap=1, dark_store=None, rider_id="R01"):
        self.env, self.store, self.id = env, dark_store, rider_id
        self.resource = simpy.Resource(env, capacity=cap)
        self.state = "available"
        self.order_key = None
        self.start = (0, 0)
        self.destination = (0, 0)
        self.departed_at = 0
        self.arrives_at = 0
        self.deliveries = 0
        self.busy_minutes = 0.0
        self.started_at = None

    def location(self, now):
        if self.state == "available":
            return (0, 0)
        duration = self.arrives_at - self.departed_at
        fraction = min(1, max(0, (now - self.departed_at) / duration)) if duration else 1
        distance = abs(self.destination[0] - self.start[0]) + abs(self.destination[1] - self.start[1])
        travelled = fraction * distance
        dx = self.destination[0] - self.start[0]
        x = self.start[0] + (1 if dx >= 0 else -1) * min(abs(dx), travelled)
        dy = self.destination[1] - self.start[1]
        y = self.start[1] + (1 if dy >= 0 else -1) * max(0, travelled - abs(dx))
        return (x, y)


def rider_factory(env, n, dark_store):
    return [Rider(env, 1, dark_store, f"R{i + 1:02d}") for i in range(n)]
