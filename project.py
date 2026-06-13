import csv
import components.customer 
import components.dark_store

# main logic of the program
def main():
    
    customers = components.customer.customer_factory()

    # write customer data (id, type, loc) in "data/customers.csv"
    with open("data/customers.csv", "a") as file:
        writer = csv.DictWriter(file, fieldnames=["id","type","loc"])
        for customer in customers:
            writer.writerow({"id": customer.id, "type": customer.type, "loc": customer.loc})
        
        