# platform will handle order reception, storing order data customer data, passing it to the delivery systems and Dark store
# platform can be thought of as the link between customers and our delivery systems
# platform administers the delivery process, hence instructs each component of the delivery system to do its work
"""
Your platform will have the methods place_order, pass it to the DarkStore
pass it to the decision system which decides the route and delivery agent
"""

from components.order import Order

class Platform:

    def __init__(self, env, city, dark_store, riders):
        self.env = env
        self.city = city
        self.dark_store = dark_store
        self.riders = riders


    # Places an order at the QComm platform
    # Called by a customer in the ordering process
    def place_order(self, customer, timestamp):
        
        # has the effect of storing the order associated data in "orders.csv" and return the order_key
        order_key = Order(customer, timestamp)

        print(f"Customer ({customer.id}) has placed an order at T = {timestamp}")
        # once the order is placed execute the logic to deliver the order.
        self.deliver(order_key)


    # The platform side orchestration logic to get an order delivered 
    def deliver(self, order_key):

        # Step1: Call sysA to decide who'll deliver the order and length of delivery path
        decision = self.system_a(self.riders, self.city, order_key)

        # Start order delivery process when the order is placed
        self.delivery(order_key)

        

    # Process of delivering an order




        ...
        