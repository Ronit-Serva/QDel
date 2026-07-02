import random
import numpy as np
# platform will handle order reception, storing order data customer data, passing it to the delivery systems and Dark store
# platform can be thought of as the link between customers and our delivery systems
# platform administers the delivery process, hence instructs each component of the delivery system to do its work
"""
Your platform will have the methods place_order, pass it to the DarkStore
pass it to the decision system which decides the route and delivery agent
"""

from components.order import Order

class Platform:

    def __init__(self, env, city, dark_store, riders, processors):
        self.env = env
        self.city = city
        self.dark_store = dark_store
        self.riders = riders
        self.processors = processors


    # Places an order at the QComm platform
    # Called by a customer in the ordering process
    def place_order(self, customer, timestamp):
        
        # has the effect of storing the order associated data in "orders.csv" and return the order_key
        order = Order(customer, timestamp)

        print(f"Customer ({customer.id}) has placed an order at T = {timestamp}")

        # once the order is placed on the platform schedule its delivery process to run at the current time
        self.env.process(self.delivery(order))

    # The delivery process 
    def delivery(self, order):

        # Step1: Call sysA to assign a rider, processor, and route to deliver the order.
        processor, rider = self.system_a(self.riders, self.city, order)

        # log the rider and processor of the order
        order.processor = processor.id
        order.rider = rider.id

        # Step2: process the order; by requesting a processor resource
        # Delivery process requests the processor resource on behalf of the given order
        
        with processor.resource.request() as req:

            yield req
            processing_time = normal_sample(mean=2.25, std=0.4, range=[1.0, 3.25])
            yield self.env.timeout(processing_time)

            # log the timestamp when the order is processed.
            order.processed_at = self.env.now
            


        # Step3: deliver the order
        with rider.resource.request() as req: 
            yield req

            # log the timestamp when the order is picked.
            order.picked_at = self.env.now

            


        

        # Step3: Occupy processor to get the order processed
        
        

        #Step4: Processor places order on dispatch tray; model as updating the order state to processed
        order.state = "processed"

        



        

        

    # Process of delivering an order




        ...

# sample a value from a normal distribution (mean,std)
# range should be of the form [a, b], such that a <= sample <= b 
def normal_sample(mean, std, range):

    a, b = range
    
    while not a <= sample <= b:
        sample = np.random.normal(loc=mean, scale=std, size=1)
    
    return round(sample[0], 2)