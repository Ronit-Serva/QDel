import simpy
import uuid
class Rider():
    def __init__(self, env, cap, dark_store):

        self.resource = simpy.Resource(env, capacity=cap)
        self.id = uuid.uuid4()
        self.env = env
        self.store = dark_store 

    ...

def rider_factory(env, n, dark_store):
    riders = []
    
    for _ in range(n):
        riders.append(Rider(env, dark_store))

