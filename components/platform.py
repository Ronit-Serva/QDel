"""FIFO packing and dispatch with riders occupied through the return trip."""
import random
import simpy

from .order import Order


def normal_sample(mean, std, range, rng=None):
    a, b = range
    if std < 0 or a > b or (std == 0 and not a <= mean <= b):
        raise ValueError("Invalid bounded normal distribution")
    if a == b:
        return a
    rng = rng or random
    while True:
        value = rng.gauss(mean, std)
        if a <= value <= b:
            return value


class Platform:
    def __init__(self, env, city, dark_store, riders, rng=None, speed_kmh=20, dispatch="fifo"):
        self.env, self.city, self.dark_store, self.riders = env, city, dark_store, riders
        self.rng = rng or random.Random()
        self.speed_kmh = speed_kmh
        self.dispatch = dispatch
        self.dispatch_slots = simpy.PriorityResource(env, capacity=len(riders))
        self.orders, self.customers, self.events = [], [], []
        self.available_processors = simpy.Store(env)
        self.available_processors.items.extend(dark_store.processors)
        self.available_riders = simpy.Store(env)
        self.available_riders.items.extend(riders)

    def record(self, order, status):
        order.status = status
        self.events.append({"time": self.env.now, "order": order.order_key, "status": status})

    def place_order(self, customer, timestamp):
        order = Order(f"QD-{len(self.orders) + 1:04d}", customer.id, customer.loc, timestamp)
        order.distance_km = self.city.route_length((0, 0), customer.loc)
        customer.state = "waiting"
        self.orders.append(order)
        self.record(order, "queued")
        self.env.process(self.delivery(order, customer))
        return order

    def delivery(self, order, customer):
        processor = yield self.available_processors.get()
        processor.started_at = self.env.now
        order.processor_id = processor.id
        order.packing_at = self.env.now
        self.record(order, "packing")
        yield self.env.timeout(normal_sample(2.25, .4, (1, 3.25), self.rng))
        processor.busy_minutes += self.env.now - processor.started_at
        processor.started_at = None
        yield self.available_processors.put(processor)
        order.ready_at = self.env.now
        self.record(order, "ready")
        priority = order.distance_km if self.dispatch == "shortest_trip" else order.timestamp
        slot = self.dispatch_slots.request(priority=priority)
        yield slot
        rider = yield self.available_riders.get()
        rider.started_at = self.env.now
        rider.order_key = order.order_key
        order.rider_id = rider.id
        order.dispatched_at = self.env.now
        self.record(order, "en_route")
        travel = order.distance_km / self.speed_kmh * 60
        self.trip(rider, "delivering", (0, 0), customer.loc, travel)
        yield self.env.timeout(travel)
        # Handoff occupies the rider, while the order is still en route.
        self.trip(rider, "handoff", customer.loc, customer.loc, .5)
        yield self.env.timeout(.5)
        order.delivered_at = self.env.now
        self.record(order, "delivered")
        customer.state = "idle"
        rider.deliveries += 1
        self.trip(rider, "returning", customer.loc, (0, 0), travel)
        yield self.env.timeout(travel)
        rider.busy_minutes += self.env.now - rider.started_at
        rider.started_at = None
        rider.state = "available"
        rider.order_key = None
        yield self.available_riders.put(rider)
        self.dispatch_slots.release(slot)

    def trip(self, rider, state, start, destination, duration):
        rider.state, rider.start, rider.destination = state, start, destination
        rider.departed_at, rider.arrives_at = self.env.now, self.env.now + duration
