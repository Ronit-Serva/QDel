class DarkStore:

    orders_db = []

    @classmethod
    def place_order(cls, customer, ordering_time):
        cls.orders_db.append((customer.id, ordering_time))
        print(f"Order recieved! Customer ID: {customer.id} Time: {ordering_time}")
        
        with open("order_data.csv", "a") as file:
            file.write(f"Customer ID: {customer.id}, Time: {ordering_time}\n")

  