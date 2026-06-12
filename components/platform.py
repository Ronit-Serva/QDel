# platform will handle order reception, storing order data customer data, passing it to the delivery systems and Dark store
# platform can be thought of as the link between customers and our delivery systems

class Platform:

    def __init__(self, env, city, dark_store):
        self.env = env
        self.city = city
        self.dark_store = dark_store

    # places an order to the QuickComm platform
    # called by a customer in the ordering process
    def place_order(self, order, customer):
        self.store 
        ...
        