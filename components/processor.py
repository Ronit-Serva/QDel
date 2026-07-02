import simpy
import uuid

class Processor:
    def __init__(self, env, dark_store):

        self.resource = simpy.Resource(env, capacity=1)
        self.id = uuid.uuid4()
        self.env = env
        self.store = dark_store
        



