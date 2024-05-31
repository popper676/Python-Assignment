import json
import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
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
    return tabulate(table, headers, tablefmt="pretty")

def show_merchant_users():
    users = load_json_data("users.json")
    table1 = []
    headers = ["Name", "Password", "Blocked", "Products"]
    for merchant_name, merchant_data in users.get("merchant", {}).items():
        table1.append([merchant_name, merchant_data['password'], merchant_data['blocked'], merchant_data['products']])
    return tabulate(table1, headers, tablefmt="pretty")

def show_traveller_users():
    users = load_json_data("users.json")
    table2 = []
    headers = ["UserName", "Password", "Blocked","Real Name", "Email"]
    for traveller_name, data in users.get("traveller", {}).items():
        table2.append([traveller_name, data['password'], data['blocked'],  data['profile']['name'],
            data['profile']['email']])
    return tabulate(table2, headers, tablefmt="pretty")

def login(user_type, username, password):
    users = load_json_data('users.json')
    if username in users[user_type] and users[user_type][username]['password'] == password:
        if not users[user_type][username].get('blocked', False):
            return True
        else:
            return "blocked"
    else:
        return False

def logout(username):
    print(f"{username} has logged out.")

def manage_users(action, user_type, username):
    users = load_json_data('users.json')
    if username in users[user_type]:
        if action == 'block':
            users[user_type][username]['blocked'] = True
        elif action == 'unblock':
            users[user_type][username]['blocked'] = False
        save_json_data('users.json', users)
        return f"User {username} has been {action}ed."
    else:
        return "User not found."

def update_promotions(promotion_details):
    promotions = load_json_data('promotions.json')
    promotions.append(promotion_details)
    save_json_data('promotions.json', promotions)
    return "Promotions updated."

def show_merchant_products(products):
    table = []
    headers = ["Merchant ID", "Product ID", "Name", "Category", "Quantity", "Price", "Schedule"]
    for merchant_id, product_list in products.items():
        for product in product_list:
            table.append([merchant_id, product['id'], product['name'], product['category'], product['quantity'], product['price'], product['schedule']])
    return tabulate(table, headers, tablefmt="pretty")

def manage_products(action, merchant_id, product_details=None, product_id=None):
    products = load_json_data('products.json')
    if merchant_id in products:
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
                return "Product not found."
        elif action == 'update' and product_details:
            for prod in products[merchant_id]:
                if prod['id'] == product_details['id']:
                    prod.update(product_details)
        else:
            return "Invalid action specified or missing product details."
        save_json_data('products.json', products)
        return f"Product has been {action}ed successfully!"
    else:
        return "Merchant not found."

def browse_destinations(criteria):
    products = load_json_data('products.json')
    matches = []
    for merchant, items in products.items():
        for item in items:
            if criteria in item['category']:
                matches.append(f"Found: {item['name']} by {merchant}")
    return matches

def view_itineraries():
    promotions = load_json_data('promotions.json')
    return [f"Promotion: {promo['title']}, Details: {promo['details']}" for promo in promotions]

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
    return f"User {user_details['username']} signed up successfully!"

def update_profile(traveller_id, profile_details, new_username, new_password):
    users = load_json_data('users.json')
    if traveller_id in users['traveller']:
        users['traveller'][traveller_id]['profile'].update(profile_details)
        users['traveller'][traveller_id]['password'] = new_password
        if traveller_id != new_username:
            users['traveller'][new_username] = users['traveller'].pop(traveller_id)
        save_json_data('users.json', users)
        return "Profile updated successfully!"
    else:
        return "Traveller not found."

def plan_trip(action, trip_details):
    bookings = load_csv_data('bookings.csv')
    if action == 'book':
        booking_id = f"b{len(bookings)}"
        bookings.append([booking_id, trip_details['traveller_id'], trip_details['product_id'], trip_details['date']])
        save_csv_data('bookings.csv', bookings)
        return "Booking successful!"
    elif action == 'cancel':
        bookings = [booking for booking in bookings if booking[0] != trip_details['booking_id']]
        save_csv_data('bookings.csv', bookings)
        return "Booking cancelled."

def recommend_trip(traveller_id, product_id):
    users = load_json_data('users.json')
    if traveller_id in users['traveller']:
        recommended_trips = users['traveller'][traveller_id].get('recommended_trips', [])
        recommended_trips.append(product_id)
        users['traveller'][traveller_id]['recommended_trips'] = recommended_trips
        save_json_data('users.json', users)
        return f"Trip {product_id} has been recommended to traveller {traveller_id} successfully!"
    else:
        return "Traveller not found."

def show_promotions():
    promotions = load_json_data("promotions.json")
    table = []
    headers = ["Title", "Details"]
    for promo in promotions:
        table.append([promo["title"], promo["details"]])
    return tabulate(table, headers, tablefmt="pretty")

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
    return tabulate(table, headers, tablefmt="pretty")

# Tkinter GUI
class KLTripPlannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KL Trip Planner Application")
        self.geometry("600x400")
        self.main_menu()

    def main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Main Menu")
        label = tk.Label(self, text="Welcome to KL Trip Planner Application", font=("Arial", 16))
        label.pack(pady=20)

        buttons = [
            ("Admin Login", self.admin_login),
            ("Merchant Login", self.merchant_login),
            ("Traveller Login", self.traveller_login),
            ("Guest", self.guest_menu),
            ("Exit", self.quit)
        ]
        for text, command in buttons:
            button = tk.Button(self, text=text, command=command, width=20)
            button.pack(pady=5)

    def admin_login(self):
        self.login('admin')

    def merchant_login(self):
        self.login('merchant')

    def traveller_login(self):
        self.login('traveller')

    def login(self, user_type):
        for widget in self.winfo_children():
            widget.destroy()
        self.title(f"{user_type.capitalize()} Login")
        label = tk.Label(self, text=f"{user_type.capitalize()} Login", font=("Arial", 16))
        label.pack(pady=20)

        username_label = tk.Label(self, text="Username:")
        username_label.pack(pady=5)
        username_entry = tk.Entry(self)
        username_entry.pack(pady=5)

        password_label = tk.Label(self, text="Password:")
        password_label.pack(pady=5)
        password_entry = tk.Entry(self, show="*")
        password_entry.pack(pady=5)

        def authenticate():
            username = username_entry.get()
            password = password_entry.get()
            result = login(user_type, username, password)
            if result == True:
                messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                if user_type == 'admin':
                    self.admin_menu(username)
                elif user_type == 'merchant':
                    self.merchant_menu(username)
                elif user_type == 'traveller':
                    self.traveller_menu(username)
            elif result == "blocked":
                messagebox.showwarning("Blocked", "Account is blocked.")
            else:
                messagebox.showerror("Invalid credentials", "Invalid credentials!")

        login_button = tk.Button(self, text="Login", command=authenticate)
        login_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=self.main_menu)
        back_button.pack(pady=5)

    def admin_menu(self, username):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Admin Menu")
        label = tk.Label(self, text="Admin Menu", font=("Arial", 16))
        label.pack(pady=20)

        buttons = [
            ("Manage Users", self.manage_users),
            ("Update Promotions", self.update_promotions),
            ("Recommend Trips", self.recommend_trips),
            ("Logout", self.main_menu)
        ]
        for text, command in buttons:
            button = tk.Button(self, text=text, command=command, width=20)
            button.pack(pady=5)

    def manage_users(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Manage Users")
        label = tk.Label(self, text="Manage Users", font=("Arial", 16))
        label.pack(pady=20)

        action_label = tk.Label(self, text="Action (block/unblock):")
        action_label.pack(pady=5)
        action_entry = tk.Entry(self)
        action_entry.pack(pady=5)

        user_type_label = tk.Label(self, text="User Type (traveller/merchant):")
        user_type_label.pack(pady=5)
        user_type_entry = tk.Entry(self)
        user_type_entry.pack(pady=5)

        user_name_label = tk.Label(self, text="Username:")
        user_name_label.pack(pady=5)
        user_name_entry = tk.Entry(self)
        user_name_entry.pack(pady=5)

        def perform_action():
            action = action_entry.get()
            user_type = user_type_entry.get()
            username = user_name_entry.get()
            result = manage_users(action, user_type, username)
            messagebox.showinfo("Result", result)

        perform_button = tk.Button(self, text="Perform Action", command=perform_action)
        perform_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=self.admin_menu)
        back_button.pack(pady=5)

    def update_promotions(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Update Promotions")
        label = tk.Label(self, text="Update Promotions", font=("Arial", 16))
        label.pack(pady=20)

        title_label = tk.Label(self, text="Promotion Title:")
        title_label.pack(pady=5)
        title_entry = tk.Entry(self)
        title_entry.pack(pady=5)

        details_label = tk.Label(self, text="Promotion Details:")
        details_label.pack(pady=5)
        details_entry = tk.Entry(self)
        details_entry.pack(pady=5)

        def update():
            title = title_entry.get()
            details = details_entry.get()
            result = update_promotions({"title": title, "details": details})
            messagebox.showinfo("Result", result)

        update_button = tk.Button(self, text="Update", command=update)
        update_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=self.admin_menu)
        back_button.pack(pady=5)

    def recommend_trips(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Recommend Trips")
        label = tk.Label(self, text="Recommend Trips", font=("Arial", 16))
        label.pack(pady=20)

        traveller_label = tk.Label(self, text="Traveller Username:")
        traveller_label.pack(pady=5)
        traveller_entry = tk.Entry(self)
        traveller_entry.pack(pady=5)

        product_label = tk.Label(self, text="Product ID to recommend:")
        product_label.pack(pady=5)
        product_entry = tk.Entry(self)
        product_entry.pack(pady=5)

        def recommend():
            traveller_id = traveller_entry.get()
            product_id = product_entry.get()
            result = recommend_trip(traveller_id, product_id)
            messagebox.showinfo("Result", result)

        recommend_button = tk.Button(self, text="Recommend", command=recommend)
        recommend_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=self.admin_menu)
        back_button.pack(pady=5)

    def merchant_menu(self, username):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Merchant Menu")
        label = tk.Label(self, text="Merchant Menu", font=("Arial", 16))
        label.pack(pady=20)

        buttons = [
            ("Manage Products", lambda: self.manage_products(username)),
            ("Logout", self.main_menu)
        ]
        for text, command in buttons:
            button = tk.Button(self, text=text, command=command, width=20)
            button.pack(pady=5)

    def manage_products(self, merchant_id):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Manage Products")
        label = tk.Label(self, text="Manage Products", font=("Arial", 16))
        label.pack(pady=20)

        action_label = tk.Label(self, text="Action (add/delete/update):")
        action_label.pack(pady=5)
        action_entry = tk.Entry(self)
        action_entry.pack(pady=5)

        product_id_label = tk.Label(self, text="Product ID (for delete/update):")
        product_id_label.pack(pady=5)
        product_id_entry = tk.Entry(self)
        product_id_entry.pack(pady=5)

        product_details_frame = tk.Frame(self)
        product_details_frame.pack(pady=5)

        product_details = {}
        fields = ["ID", "Name", "Category", "Quantity", "Price", "Schedule"]
        for field in fields:
            frame = tk.Frame(product_details_frame)
            frame.pack(pady=2)
            label = tk.Label(frame, text=f"{field}:")
            label.pack(side=tk.LEFT)
            entry = tk.Entry(frame)
            entry.pack(side=tk.RIGHT)
            product_details[field.lower()] = entry

        def perform_action():
            action = action_entry.get()
            product_id = product_id_entry.get()
            details = {field: product_details[field].get() for field in product_details}
            if action == "add":
                details["quantity"] = int(details["quantity"])
                details["price"] = float(details["price"])
            result = manage_products(action, merchant_id, details, product_id)
            messagebox.showinfo("Result", result)

        perform_button = tk.Button(self, text="Perform Action", command=perform_action)
        perform_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=lambda: self.merchant_menu(merchant_id))
        back_button.pack(pady=5)

    def traveller_menu(self, username):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Traveller Menu")
        label = tk.Label(self, text="Traveller Menu", font=("Arial", 16))
        label.pack(pady=20)

        buttons = [
            ("Update Profile", lambda: self.update_profile(username)),
            ("Plan a Trip", lambda: self.plan_trip(username)),
            ("Show Trip Details", lambda: self.show_trip_details(username)),
            ("Logout", self.main_menu)
        ]
        for text, command in buttons:
            button = tk.Button(self, text=text, command=command, width=20)
            button.pack(pady=5)

    def update_profile(self, username):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Update Profile")
        label = tk.Label(self, text="Update Profile", font=("Arial", 16))
        label.pack(pady=20)

        profile_details = {}
        fields = ["New Username", "New Password", "Name", "Email"]
        for field in fields:
            frame = tk.Frame(self)
            frame.pack(pady=5)
            label = tk.Label(frame, text=f"{field}:")
            label.pack(side=tk.LEFT)
            entry = tk.Entry(frame)
            entry.pack(side=tk.RIGHT)
            profile_details[field.lower().replace(" ", "_")] = entry

        def update():
            details = {field: profile_details[field].get() for field in profile_details}
            result = update_profile(username, {"name": details["name"], "email": details["email"]}, details["new_username"], details["new_password"])
            messagebox.showinfo("Result", result)

        update_button = tk.Button(self, text="Update", command=update)
        update_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=lambda: self.traveller_menu(username))
        back_button.pack(pady=5)

    def plan_trip(self, username):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Plan a Trip")
        label = tk.Label(self, text="Plan a Trip", font=("Arial", 16))
        label.pack(pady=20)

        action_label = tk.Label(self, text="Action (book/cancel):")
        action_label.pack(pady=5)
        action_entry = tk.Entry(self)
        action_entry.pack(pady=5)

        trip_details = {}
        fields = ["Product ID", "Date (YYYY-MM-DD)", "Booking ID (for cancel)"]
        for field in fields:
            frame = tk.Frame(self)
            frame.pack(pady=5)
            label = tk.Label(frame, text=f"{field}:")
            label.pack(side=tk.LEFT)
            entry = tk.Entry(frame)
            entry.pack(side=tk.RIGHT)
            trip_details[field.lower().replace(" ", "_")] = entry

        def perform_action():
            action = action_entry.get()
            details = {field: trip_details[field].get() for field in trip_details}
            result = plan_trip(action, {"traveller_id": username, "product_id": details["product_id"], "date": details["date"], "booking_id": details["booking_id"]})
            messagebox.showinfo("Result", result)

        perform_button = tk.Button(self, text="Perform Action", command=perform_action)
        perform_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=lambda: self.traveller_menu(username))
        back_button.pack(pady=5)

    def show_trip_details(self, username):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Show Trip Details")
        label = tk.Label(self, text="Trip Details", font=("Arial", 16))
        label.pack(pady=20)

        details = show_trip_details(username)
        text = tk.Text(self)
        text.pack(pady=10)
        text.insert(tk.END, details)

        back_button = tk.Button(self, text="Back", command=lambda: self.traveller_menu(username))
        back_button.pack(pady=5)

    def guest_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Guest Menu")
        label = tk.Label(self, text="Guest Menu", font=("Arial", 16))
        label.pack(pady=20)

        buttons = [
            ("Browse Destinations", self.browse_destinations),
            ("View Itineraries", self.view_itineraries),
            ("Sign Up", self.sign_up),
            ("Back", self.main_menu)
        ]
        for text, command in buttons:
            button = tk.Button(self, text=text, command=command, width=20)
            button.pack(pady=5)

    def browse_destinations(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Browse Destinations")
        label = tk.Label(self, text="Browse Destinations", font=("Arial", 16))
        label.pack(pady=20)

        criteria_label = tk.Label(self, text="Search Criteria:")
        criteria_label.pack(pady=5)
        criteria_entry = tk.Entry(self)
        criteria_entry.pack(pady=5)

        def browse():
            criteria = criteria_entry.get()
            results = browse_destinations(criteria)
            text = tk.Text(self)
            text.pack(pady=10)
            text.insert(tk.END, results)

        browse_button = tk.Button(self, text="Browse", command=browse)
        browse_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=self.guest_menu)
        back_button.pack(pady=5)

    def view_itineraries(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("View Itineraries")
        label = tk.Label(self, text="Itineraries", font=("Arial", 16))
        label.pack(pady=20)

        details = view_itineraries()
        text = tk.Text(self)
        text.pack(pady=10)
        text.insert(tk.END, details)

        back_button = tk.Button(self, text="Back", command=self.guest_menu)
        back_button.pack(pady=5)

    def sign_up(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.title("Sign Up")
        label = tk.Label(self, text="Sign Up", font=("Arial", 16))
        label.pack(pady=20)

        user_details = {}
        fields = ["Username", "Password", "Name", "Email"]
        for field in fields:
            frame = tk.Frame(self)
            frame.pack(pady=5)
            label = tk.Label(frame, text=f"{field}:")
            label.pack(side=tk.LEFT)
            entry = tk.Entry(frame)
            entry.pack(side=tk.RIGHT)
            user_details[field.lower()] = entry

        def sign_up_user():
            details = {field: user_details[field].get() for field in user_details}
            result = sign_up(details)
            messagebox.showinfo("Result", result)

        sign_up_button = tk.Button(self, text="Sign Up", command=sign_up_user)
        sign_up_button.pack(pady=20)

        back_button = tk.Button(self, text="Back", command=self.guest_menu)
        back_button.pack(pady=5)

if __name__ == "__main__":
    app = KLTripPlannerApp()
    app.mainloop()
