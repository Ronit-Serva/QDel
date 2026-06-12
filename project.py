import components.customer 
import components.dark_store

# main logic of the program
def main():
    
    customers = components.customer.customer_factory()

    # write customer data (id, loc) "data/customers.csv"
    with open("data/customers.csv", "a") as file:
        file.write("id, location")
        for customer in customers:
            file.write(f"{customer.id}, {customer.loc}")
        