import customtkinter as ctk
import tkinter
from tkinter import messagebox
import json
import bcrypt
from datetime import datetime
import os
import random
import re

# Ensure the users.json file exists
def create_users_file_if_not_exists():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as file:
            json.dump({}, file)

def load_users():
    with open("users.json", "r") as file:
        return json.load(file)

def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

def generate_account_number(users):
    while True:
        account_number = random.randint(1000000000, 9999999999)
        if not any('account_number' in user and user['account_number'] == account_number for user in users.values()):
            return account_number

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def determine_gender(id_number):
    seventh_digit = int(id_number[6])
    return "female" if seventh_digit % 2 == 0 else "male"

def calculate_maintenance_fee(account_type):
    return 50.00 if account_type == "savings" else 100.00

def calculate_transaction_fee(account_type):
    return 5.00 if account_type == "savings" else 10.00

create_users_file_if_not_exists()

class CitieBankingApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Citie Banking")
        self.geometry("800x600")

        self.username = None

        self.login_frame = LoginFrame(self, self.show_register_frame, self.login_success)
        self.register_frame = RegisterFrame(self, self.show_login_frame, self.register_user)
        self.dashboard_frame = DashboardFrame(self, self.logout)

        self.login_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        self.geometry("600x480")
        self.register_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def show_register_frame(self):
        self.geometry("800x700")
        self.login_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        self.register_frame.pack(fill="both", expand=True)

    def login_success(self, username):
        self.username = username
        self.login_frame.pack_forget()
        self.register_frame.pack_forget()
        self.dashboard_frame.pack(fill="both", expand=True)
        self.dashboard_frame.update_user_info(username)

    def register_user(self, user_data):
        users = load_users()
        users[user_data["username"]] = user_data
        save_users(users)
        self.show_login_frame()

    def logout(self):
        self.username = None
        self.dashboard_frame.pack_forget()
        self.show_login_frame()

class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent, show_register, login_success):
        super().__init__(parent)

        self.show_register = show_register
        self.login_success = login_success

        self.label = ctk.CTkLabel(self, text="Login", font=("Arial", 24))
        self.label.pack(pady=12)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=12)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=12)

        self.login_button = ctk.CTkButton(self, text="Login", command=self.authenticate_user)
        self.login_button.pack(pady=12)

        self.register_label = ctk.CTkLabel(self, text="Don't have an account?")
        self.register_label.pack(pady=6)
        self.register_button = ctk.CTkButton(self, text="Register", command=self.show_register)
        self.register_button.pack(pady=6)

    def authenticate_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        users = load_users()
        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]["password"].encode('utf-8')):
            if not users[username].get("maintenance_fee_deducted", False):
                account_type = users[username]["account_type"]
                maintenance_fee = calculate_maintenance_fee(account_type)
                users[username]["balance"] -= maintenance_fee
                users[username]["maintenance_fee_deducted"] = True
                transaction_record = f"Maintenance fee of R{maintenance_fee:.2f} deducted at {datetime.now()}"
                users[username]["transactions"].append(transaction_record)
                save_users(users)
                messagebox.showinfo("Maintenance fee", f"Maintenance fee of R{maintenance_fee:.2f} has been deducted from your account.")
            self.login_success(username)
        else:
            messagebox.showerror("Invalid username or password")

class RegisterFrame(ctk.CTkFrame):

    def __init__(self, parent, show_login, register_user):
        super().__init__(parent)

        self.show_login = show_login
        self.register_user = register_user

        self.label = ctk.CTkLabel(self, text="Register", font=("Arial", 24))
        self.label.pack(pady=12)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.username_entry.pack(pady=12)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=12)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email")
        self.email_entry.pack(pady=12)

        self.first_name_entry = ctk.CTkEntry(self, placeholder_text="First Name")
        self.first_name_entry.pack(pady=12)

        self.last_name_entry = ctk.CTkEntry(self, placeholder_text="Last Name")
        self.last_name_entry.pack(pady=12)

        self.id_number_entry = ctk.CTkEntry(self, placeholder_text="ID Number")
        self.id_number_entry.pack(pady=12)

        self.account_type_option = ctk.CTkOptionMenu(self, values=["savings", "cheque"])
        self.account_type_option.pack(pady=12)

        self.register_button = ctk.CTkButton(self, text="Register", command=self.register)
        self.register_button.pack(pady=12)

        self.login_label = ctk.CTkLabel(self, text="Already have an account?")
        self.login_label.pack(pady=6)
        self.login_button = ctk.CTkButton(self, text="Login", command=self.show_login)
        self.login_button.pack(pady=6)

    def register(self):
        users = load_users()

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        id_number = self.id_number_entry.get().strip()
        account_type = self.account_type_option.get()

        if not username or username in users:
            messagebox.showerror("Username Error", "Username already exists or is empty. Please choose another one.")
            return

        if len(password) < 8:
            messagebox.showerror("Password Error", "Password must be at least 8 characters long.")
            return

        if not is_valid_email(email):
            messagebox.showerror("Email Error", "Invalid email format. Please enter a valid email.")
            return

        if not first_name.isalpha() or not first_name:
            messagebox.showerror("First Name Error", "First name must contain only alphabetic characters and cannot be empty.")
            return

        if not last_name.isalpha() or not last_name:
            messagebox.showerror("Last Name Error", "Last name must contain only alphabetic characters and cannot be empty.")
            return

        if not id_number.isdigit() or len(id_number) != 13:
            messagebox.showerror("ID Number Error", "Invalid ID number. Please enter a valid 13-digit ID number.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        account_number = generate_account_number(users)
        gender = determine_gender(id_number)

        user_data = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "id_number": id_number,
            "account_type": account_type,
            "account_number": account_number,
            "balance": 0.0,
            "transactions": [],
            "messages": [],
            "maintenance_fee_deducted": False
        }

        self.register_user(user_data)

class DashboardFrame(ctk.CTkFrame):

    def __init__(self, parent, logout):
        super().__init__(parent)
        self.logout = logout
        self.username = None

