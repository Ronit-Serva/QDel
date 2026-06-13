import csv
import uuid
# class for instantiating an order object
class Order:
    def __init__(self, customer, timestamp):

        """
        this will write the order data in "data/orders.csv" and assign
        the generated order_key to the corresponding attribute. It can
        give you access to read and modify order data
        """
        self.order_key = self.write_order(customer, timestamp)
    
    def write_order(customer, timestamp):
        with open("data/orders.csv", "a") as file:
            writer = csv.DictWriter(file, fieldnames=["order_key","customer_id","customer_type","customer_loc","timestamp"])
            order_key = uuid.uuid4()
            writer.writerow({"order_key": order_key,"customer_id": customer.id,"customer_type": customer.type,"customer_loc": customer.loc,"timestamp": timestamp})
        
        return order_key


    # index into orders.csv and return the order dict containing order data of the specific order
    # index with help of order_key attribute
    def read_order(self):

        with open("data/orders.csv", "r") as file:

            reader = csv.DictReader(file)

            for row in reader:
                if row[0] == self.order_key:
                    return row
                
    """
    We can implement other methods that allow us to modify the order data values
    as required
    """