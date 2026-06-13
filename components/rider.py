import uuid
class Rider():
    def __init__(self, env, dark_store):
        self.env = env
        self.dark_store = dark_store

        # order_queue to store all the pending orders assigned to the rider
        self.order_queue = []
        self.rider_id = uuid.uuid4() 

    ...

def rider_factory(env, n, dark_store):
    riders = []
    
    for _ in range(n):
        riders.append(Rider(env, dark_store))

