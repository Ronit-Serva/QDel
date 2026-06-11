import uuid
import simpy
import random

def main():
    city_grid = CityGrid(side_km=10, num_parallel_streets=5)
    print(city_grid.locs)


class CityGrid:
    def __init__(self, side_km: int, num_parallel_streets: int):

        self.side = side_km
        self.num_parallel_streets = num_parallel_streets
        # remove the loc of the dark store from the list of available locs for customers
        self.customer_locs = self.generate_locs().remove((0,0)) 
        # the loc of the dark store is fixed at the center of the city grid
        self.dark_store_loc = (0,0) 
        # to keep track of assigned locs to customers 
        self.assigned_locs = [] 
    
    #generate the list of all available locs in the city grid
    def generate_locs(self):
        locs = []
        min_length = self.side / self.num_parallel_streets

        i = (1 - self.num_parallel_streets) / 2
        while i != (self.num_parallel_streets + 1) / 2:
            
            j = (1 - self.num_parallel_streets) / 2
            while j != (self.num_parallel_streets + 1)/ 2:
                locs.append((i * min_length, j * min_length))
                j += 1
            i += 1
        return locs
    
    # Sample a random locaton from the city grid; this can be used to assign a loc to a customer
    def sample(self):
        # first sample a random loc from the list of locs
        r = random.Random()
        sampled_loc = r.choice(self.locs)
        
        # then migrate it from "locs" to the "assigned_locs" list to keep track of it
        self.locs.remove(sampled_loc)
        self.assigned_locs.append(sampled_loc)

        # then return the sampled loc
        return sampled_loc
    
    # return manhattan distance between two locs; treat it as the optimal route length.
    @classmethod
    def route_length(cls, loc1, loc2):
        return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
    

class Customer:
    def __init__(self, env, loc):
        self.state = "idle"
        self.env = env
        self.loc = loc
        self.id = uuid.uuid4()
        self.action = env.process(self.run())

    # The main process of a customer
    def run(self):
        while True:
            self.state = "idle"
            yield self.env.timeout(10)
            self.state = "ordering"
            # suspend the process until ordering process is complete
            yield self.env.process(self.order())
            # some delay after the customr has ordered; 
            # this delay can be thought of as the time it takes to deliver the order
            yield self.env.timeout(5)

    # ordering process of a customer; 
    # will handle placing an order based on the items available in the dark store
    def order(self):
        # Simulate the time taken to place an order
        yield self.env.timeout(2)


# Creates desried number of customers by assigning them random locs in the city grid;
# Each loc can be assigned to 4 customers as each location corresponds to a crossing which corresponds to 4 houses

def customer_factory(env, num_customers, city_grid):

    customers = []
    for _ in range(num_customers):
        customers.append(Customer(env, city_grid.sample()))

    
    

if __name__ == "__main__":
    main()