import pymysql
import random
from datetime import datetime, timedelta

# Database Configuration
db_config = {
    "host": "sql12.freesqldatabase.com",         # e.g., "localhost"
    "user": "sql12766815",         # e.g., "root"
    "password": "ZvPV8XPsBs", # e.g., "your_password"
    "database": "sql12766815", # e.g., "sales_db"
}



# Connect to MySQL database
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# Helper function to fetch IDs
def fetch_ids(table, column):
    cursor.execute(f"SELECT {column} FROM {table}")
    return [row[0] for row in cursor.fetchall()]

# Fetch available customer and product IDs
customer_ids = fetch_ids("Customers", "CustomerID")
product_ids = fetch_ids("Products", "ProductID")

# Define payment methods
payment_methods = ['Cash', 'Credit Card', 'Debit Card', 'Online Transfer']

# Generate random sales data for the past year
start_date = datetime.today() - timedelta(days=30)
end_date = datetime.today()

current_date = start_date
while current_date <= end_date:
    # Random number of sales per day (1 to 10)
    num_sales = random.randint(1, 50)

    for _ in range(num_sales):
        try:
            # Select random customer
            customer_id = random.choice(customer_ids)

            # Random number of products in sale (1 to 5)
            num_products = random.randint(1, 5)
            
            sale_products = random.sample(product_ids, num_products)

            # Insert Sale Record
            payment_method = random.choice(payment_methods)
            total_amount = 0.0
            status = random.choice(['Completed', 'Pending', 'Cancelled'])

            cursor.execute("""
                INSERT INTO Sales (CustomerID, SaleDate, TotalAmount, PaymentMethod, Status) 
                VALUES (%s, %s, %s, %s, %s)
            """, (customer_id, current_date, total_amount, payment_method, status))
            conn.commit()
            sale_id = cursor.lastrowid  # Get inserted SaleID

            # Insert Sale Details and calculate total
            total_sale_amount = 0.0
            for product_id in sale_products:
                quantity = random.randint(1, 3)  # Quantity per product
                cursor.execute("SELECT Price FROM Products WHERE ProductID = %s", (product_id,))
                unit_price = cursor.fetchone()[0]
                subtotal = quantity * unit_price
                total_sale_amount += float(subtotal)

                cursor.execute("""
                    INSERT INTO SalesDetails (SaleID, ProductID, Quantity, UnitPrice, SubTotal) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (sale_id, product_id, quantity, unit_price, subtotal))
            
            # Update total amount in Sales table
            cursor.execute("UPDATE Sales SET TotalAmount = %s WHERE SaleID = %s", (total_sale_amount, sale_id))

            # Insert Payment if status is 'Completed'
            if status == 'Completed':
                transaction_id = f"TXN{random.randint(100000, 999999)}"
                cursor.execute("""
                    INSERT INTO Payments (SaleID, PaymentDate, Amount, PaymentMethod, TransactionID) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (sale_id, current_date, total_sale_amount, payment_method, transaction_id))
            print("""VALUES (%s, %s, %s, %s, %s)""", (sale_id, current_date, total_sale_amount, payment_method, transaction_id))
            conn.commit()
        except Exception as e:
            print(f"Error inserting sale data: {e}")
            # conn.rollback()
    # Move to the next day
    current_date += timedelta(days=1)

# Close connections
cursor.close()
conn.close()

print("Sales data populated successfully!")
