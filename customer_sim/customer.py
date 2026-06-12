import uuid
import simpy
import random

def main():
    city_grid = CityGrid(side_km=10, num_parallel_streets=5)
    env = simpy.Environment()
    customers = customer_factory(env, num_customers=24, city_grid=city_grid)
    
    env.run(until=1440)
    


class CityGrid:
    #num_parallel_streets must me an odd number
    def __init__(self, side_km: int, num_parallel_streets: int):

        self.side = side_km
        self.num_parallel_streets = num_parallel_streets
        
        self.customer_locs = self.generate_locs()
        # the loc of the dark store is fixed at the center of the city grid
        self.dark_store_loc = (0.0, 0.0) 
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

        # remove the loc of the dark store from the list of available locs for customer assignment
        locs.remove((0.0, 0.0))
        return locs
    
    # Sample a random locaton from the city grid; this can be used to assign a loc to a customer
    def sample_loc(self):
        # first sample a random loc from the list of locs
        r = random.Random()
        
        sampled_loc = r.choice(self.customer_locs)
        
        # then migrate it from "locs" to the "assigned_locs" list to keep track of it
        self.customer_locs.remove(sampled_loc)
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
            r = random.Random()

            # Simulate the time customer is idle
            idle_time = r.randint(5, 15)  
            yield self.env.timeout(idle_time)
            self.state = "ordering"
            print(f"Customer ({self.id}) is going to place an order at T = {self.env.now}")
            # suspend the process until ordering process is complete
            yield self.env.process(self.order())
            # some delay after the customr has ordered; 
            # this delay can be thought of as the time it takes to deliver the order
            yield self.env.timeout(20)
            

    # ordering process of a customer; 
    # will handle placing an order based on the items available in the dark store
    def order(self):
        # Simulate the time taken to place an order
        r = random.Random()
        ordering_time = r.randint(1, 5)  
        yield self.env.timeout(ordering_time)
        # Logic to place an order directly to the dark store.
        custom = self
        DarkStore.place_order(customer=custom, ordering_time=self.env.now)
        print(f"Customer ({self.id}) has placed an order at T = {self.env.now}")

class DarkStore:
    orders_db = []

    @classmethod
    def place_order(cls, customer, ordering_time):
        cls.orders_db.append((customer.id, ordering_time))
        print(f"Order recieved! Customer ID: {customer.id} Time: {ordering_time}")
        
        with open("order_data.csv", "a") as file:
            file.write(f"Customer ID: {customer.id}, Time: {ordering_time}\n")

    



# Creates desried number of customers by assigning them random locs in the city grid;
# Each loc can be assigned to 4 customers as each location corresponds to a crossing which corresponds to 4 houses

def customer_factory(env, num_customers, city_grid):

    customers = []
    for _ in range(num_customers):
        customers.append(Customer(env, city_grid.sample_loc()))

    
    

if __name__ == "__main__":
    main()