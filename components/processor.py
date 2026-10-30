import simpy


class Processor:
    def __init__(self, env, dark_store, processor_id):
        self.env, self.store, self.id = env, dark_store, processor_id
        self.resource = simpy.Resource(env, capacity=1)
        self.busy_minutes = 0.0
        self.started_at = None
