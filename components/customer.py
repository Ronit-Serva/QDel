import math
import uuid
import random
from city_model import CityGrid

def main():
    ...

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
        DarkStore.place_order(customer=custom, ordering_time=self.env.now)
        print(f"Customer ({self.id}) has placed an order at T = {self.env.now}")

  

# Creates desried number of customers by assigning them random locs in the city grid;
# Each loc can be assigned to 4 customers as each location corresponds to a crossing which corresponds to 4 houses
# num_customers should be such that num_customers = 4(n**2-1), n belong integer
def customer_factory(env, num_customers):

    x = (num_customers / 4) + 1 
    city_grid = CityGrid(side_km=4, num_parallel_streets=math.sqrt(x))

    customers = []
    for _ in range(num_customers/4):
        loc = city_grid.sample_loc()
        #assigns one location to 4 customers
        for _ in range(4):
            customers.append(Customer(env, loc=loc))
    return customers

    
    

if __name__ == "__main__":
    main()