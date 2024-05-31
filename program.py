import json
import csv
import os
from tabulate import tabulate

# Define the base directory where data files are located
base_dir = os.path.join(os.path.dirname(__file__), 'data')

# Load data from JSON files
def load_json_data(filename):
    filepath = os.path.join(base_dir, filename)
    print(f"Trying to open file at: {filepath}")  # Debug statement
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {filepath}")
        return {}

# Save data to JSON files
def save_json_data(filename, data):
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# Load data from CSV file
def load_csv_data(filename):
    filepath = os.path.join(base_dir, filename)
    try:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []

# Save data to CSV file
def save_csv_data(filename, data):
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

# Function to show all products
def show_products():
    products = load_json_data('products.json')
    table = []
    headers = ["Merchant ID", "Product ID", "Name", "Category", "Quantity", "Price", "Schedule"]
    for merchant_id, items in products.items():
        for item in items:
            table.append([merchant_id, item['id'], item['name'], item['category'], item['quantity'], item['price'], item['schedule']])
    print(tabulate(table, headers, tablefmt="pretty"))

def show_merchant_users():
    users = load_json_data("users.json")
    table1 = []
    headers = ["Name", "Password", "Blocked", "Products"]
    for merchant_name, merchant_data in users.get("merchant", {}).items():
        table1.append([merchant_name, merchant_data['password'], merchant_data['blocked'], merchant_data['products']])
    print(tabulate(table1, headers, tablefmt="pretty"))

def show_traveller_users():
    users = load_json_data("users.json")
    table2 = []
    headers = ["UserName", "Password", "Blocked","Real Name", "Email"]
    for traveller_name, data in users.get("traveller", {}).items():
        table2.append([traveller_name, data['password'], data['blocked'],  data['profile']['name'],
            data['profile']['email']])
    print(tabulate(table2, headers, tablefmt="pretty"))
# User Authentication
def login(user_type, username, password):
    users = load_json_data('users.json')
    if username in users[user_type] and users[user_type][username]['password'] == password:
        if not users[user_type][username].get('blocked', False):
            print(f"Welcome, {username}!")
            return True
        else:
            print("Account is blocked.")
            return False
    else:
        print("Invalid credentials!")
        return False

def logout(username):
    print(f"{username} has logged out.")

# Admin Functions
def manage_users(action, user_type, username):
    users = load_json_data('users.json')
    if username in users[user_type]:
        if action == 'block':
            users[user_type][username]['blocked'] = True
        elif action == 'unblock':
            users[user_type][username]['blocked'] = False
        save_json_data('users.json', users)
        print(f"User {username} has been {action}ed.")
    else:
        print("User not found.")

def update_promotions(promotion_details):
    promotions = load_json_data('promotions.json')
    promotions.append(promotion_details)
    save_json_data('promotions.json', promotions)
    print("Promotions updated.")

def show_merchant_products(products):
    print("+-------------+------------+------------------------+---------------+----------+-------+-------------------------+")
    print("| Merchant ID | Product ID |          Name          |   Category    | Quantity | Price |        Schedule         |")
    print("+-------------+------------+------------------------+---------------+----------+-------+-------------------------+")
    for merchant_id, product_list in products.items():
        for product in product_list:
            print(f"| {merchant_id:^11} | {product['id']:^10} | {product['name']:^22} | {product['category']:^13} | {product['quantity']:^8} | {product['price']:^5} | {product['schedule']:^23} |")
    print("+-------------+------------+------------------------+---------------+----------+-------+-------------------------+")

# Merchant Functions
def manage_products(action, merchant_id, product_details=None, product_id=None):
    products = load_json_data('products.json')

    if merchant_id in products:
        show_merchant_products(products)  # Show products before managing them

        if action == 'add' and product_details:
            products[merchant_id].append(product_details)
        elif action == 'delete' and product_id:
            deleted = False
            for prod in products[merchant_id]:
                if prod['id'] == product_id:
                    products[merchant_id].remove(prod)
                    deleted = True
                    break
            if not deleted:
                print("Product not found.")
                return
        elif action == 'update' and product_details:
            for prod in products[merchant_id]:
                if prod['id'] == product_details['id']:
                    prod.update(product_details)
        else:
            print("Invalid action specified or missing product details.")
            return

        save_json_data('products.json', products)
        print(f"Product has been {action}ed successfully!")
    else:
        print("Merchant not found.")


# Guest Functions
def browse_destinations(criteria):
    products = load_json_data('products.json')
    for merchant, items in products.items():
        for item in items:
            if criteria in item['category']:
                print(f"Found: {item['name']} by {merchant}")

def view_itineraries():
    promotions = load_json_data('promotions.json')
    for promo in promotions:
        print(f"Promotion: {promo['title']}, Details: {promo['details']}")

def sign_up(user_details):
    users = load_json_data('users.json')
    users['traveller'][user_details['username']] = {
        "password": user_details['password'],
        "blocked": False,
        "profile": {
            "name": user_details['name'],
            "email": user_details['email']
        }
    }
    save_json_data('users.json', users)
    print(f"User {user_details['username']} signed up successfully!")

# Traveller Functions
def update_profile(traveller_id, profile_details, new_username, new_password):
    users = load_json_data('users.json')

    if traveller_id in users['traveller']:
        # Update the profile details
        users['traveller'][traveller_id]['profile'].update(profile_details)

        # Update the password
        users['traveller'][traveller_id]['password'] = new_password

        # If the username is changing, handle the change
        if traveller_id != new_username:
            users['traveller'][new_username] = users['traveller'].pop(traveller_id)

        save_json_data('users.json', users)
        print("Profile updated successfully!")
    else:
        print("Traveller not found.")

def plan_trip(action, trip_details):
    bookings = load_csv_data('bookings.csv')
    if action == 'book':
        booking_id = f"b{len(bookings)}"
        bookings.append([booking_id, trip_details['traveller_id'], trip_details['product_id'], trip_details['date']])
        save_csv_data('bookings.csv', bookings)
        print("Booking successful!")
    elif action == 'cancel':
        bookings = [booking for booking in bookings if booking[0] != trip_details['booking_id']]
        save_csv_data('bookings.csv', bookings)
        print("Booking cancelled.")

def recommend_trip(traveller_id, product_id):
    users = load_json_data('users.json')
    products = load_json_data('products.json')

    if traveller_id in users['traveller']:
        recommended_trips = users['traveller'][traveller_id].get('recommended_trips', [])
        recommended_trips.append(product_id)
        users['traveller'][traveller_id]['recommended_trips'] = recommended_trips
        save_json_data('users.json', users)
        print(f"Trip {product_id} has been recommended to traveller {traveller_id} successfully!")
    else:
        print("Traveller not found.")

# Function to show promotions data
def show_promotions():
    promotions = load_json_data("promotions.json")
    table = []
    headers = ["Title", "Details"]
    for promo in promotions:
        table.append([promo["title"], promo["details"]])
    print(tabulate(table, headers, tablefmt="pretty"))

def show_trip_details(traveller_id):
    bookings = load_csv_data('bookings.csv')
    products = load_json_data('products.json')
    traveller_bookings = [booking for booking in bookings if booking[1] == traveller_id]
    table = []
    headers = ["Booking ID", "Product ID", "Product Name", "Category", "Date"]
    for booking in traveller_bookings:
        product_id = booking[2]
        date = booking[3]
        for merchant_id, items in products.items():
            for item in items:
                if item['id'] == product_id:
                    table.append([booking[0], product_id, item['name'], item['category'], date])
    print(tabulate(table, headers, tablefmt="pretty"))

# Main Function to Run the Program
def main():
    while True:
        print("\nWelcome to KL Trip Planner Application")
        print("1. Admin Login")
        print("2. Merchant Login")
        print("3. Traveller Login")
        print("4. Guest")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")
            if login('admin', username, password):
                while True:
                    print("\nAdmin Menu")
                    print("1. Manage Users")
                    print("2. Update Promotions")
                    print("3. Recommend Trips")
                    print("4. Logout")
                    admin_choice = input("Enter your choice: ")

                    if admin_choice == '1':
                        action = input("Enter action (block/unblock): ")
                        user_type = input("Enter user type (traveller/merchant): ")
                        if user_type == "merchant":
                            show_merchant_users()
                            user_name = input("Enter username: ")
                            manage_users(action, user_type, user_name)
                            show_merchant_users()
                        elif user_type == "traveller":
                            show_traveller_users()
                            user_name = input("Enter username: ")
                            manage_users(action, user_type, user_name)
                            show_traveller_users()
                        else:
                            print("Wrong selection")
                    elif admin_choice == '2':
                        show_promotions()
                        title = input("Enter promotion title: ")
                        details = input("Enter promotion details: ")
                        update_promotions({"title": title, "details": details})
                    elif admin_choice == '3':
                        show_traveller_users()
                        traveller_id = input("Enter traveller Username: ")
                        show_products()
                        product_id = input("Enter product ID to recommend: ")
                        recommend_trip(traveller_id, product_id)
                    elif admin_choice == '4':
                        logout(username)
                        break

        elif choice == '2':
            username = input("Enter merchant username: ")
            password = input("Enter merchant password: ")
            if login('merchant', username, password):
                while True:
                    print("\nMerchant Menu")
                    print("1. Manage Products")
                    print("2. Logout")
                    merchant_choice = input("Enter your choice: ")

                    if merchant_choice == '1':
                        show_products()  # Show products before managing them
                        if merchant_choice == '1':
                            action = input("Enter action (add/delete/update): ")
                            if action == 'delete':
                                product_id = input("Enter product ID: ")
                                manage_products(action, username, product_id=product_id)
                            else:
                                product_details = {
                                    "id": input("Enter product ID: "),
                                    "name": input("Enter product name: "),
                                    "category": input("Enter product category: "),
                                    "quantity": int(input("Enter product quantity: ")),
                                    "price": float(input("Enter product price: ")),
                                    "schedule": input("Enter product schedule: ")
                                }
                                manage_products(action, username, product_details)

                    elif merchant_choice == '2':
                        logout(username)
                        break

        elif choice == '3':
            username = input("Enter traveller username: ")
            password = input("Enter traveller password: ")
            if login('traveller', username, password):
                while True:
                    print("\nTraveller Menu")
                    print("1. Update Profile")
                    print("2. Plan a Trip")
                    print("3. Show Trip Details")
                    print("4. Logout")
                    traveller_choice = input("Enter your choice: ")

                    if traveller_choice == '1':
                        new_username = input("Enter new Username: ")
                        new_password = input("Change Password: ")
                        profile_details = {
                            "name": input("Enter new name: "),
                            "email": input("Enter new email: ")
                        }
                        update_profile(username, profile_details, new_username, new_password)
                        # Update the username for subsequent operations
                        username = new_username

                    elif traveller_choice == '2':
                        action = input("Enter action (book/cancel): ")
                        if action == 'book':
                            products = load_json_data('products.json')
                            print("Available Products:")
                            show_products()  # Show products before booking
                            trip_details = {
                                "traveller_id": username,
                                "product_id": input("Enter product ID: "),
                                "date": input("Enter date (YYYY-MM-DD): ")
                            }
                        elif action == 'cancel':
                            trip_details = {
                                "traveller_id": username,
                                "booking_id": input("Enter booking ID: ")
                            }
                        plan_trip(action, trip_details)
                    elif traveller_choice == '3':
                        show_trip_details(username)
                    elif traveller_choice == '4':
                        logout(username)
                        break

        elif choice == '4':
            print("\nGuest Menu")
            print("1. Browse Destinations")
            print("2. View Itineraries")
            print("3. Sign Up")
            guest_choice = input("Enter your choice: ")

            if guest_choice == '1':
                criteria = input("Enter search criteria: ")
                browse_destinations(criteria)
            elif guest_choice == '2':
                view_itineraries()
            elif guest_choice == '3':
                user_details = {
                    "username": input("Enter username: "),
                    "password": input("Enter password: "),
                    "name": input("Enter name: "),
                    "email": input("Enter email: ")
                }
                sign_up(user_details)

        elif choice == '5':
            print("Exiting the application. Goodbye!")
            break

        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
