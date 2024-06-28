import openai
from email.mime import image
import customtkinter as ctk
from customtkinter import *
import tkinter
from PIL import Image
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
        ctk.set_appearance_mode("light")
        set_default_color_theme("green")
        self.title("Citie Banking")
        self.geometry("800x600")
        self.resizable(0,0)

        self.username = None

        self.login_frame = LoginFrame(self, self.show_register_frame, self.login_success)
        self.register_frame = RegisterFrame(self, self.show_login_frame, self.register_user)
        self.dashboard_frame = DashboardFrame(self, self.logout)

        self.login_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        self.geometry("1024×768")
        self.register_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def show_register_frame(self):
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

        # Load images
        side_img_data = Image.open("Untitled.png")
        email_icon_data = Image.open("uname.png")
        password_icon_data = Image.open("lcok.png")

        side_img = ctk.CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(400, 480))
        email_icon = ctk.CTkImage(dark_image=email_icon_data, light_image=email_icon_data, size=(20, 20))
        password_icon = ctk.CTkImage(dark_image=password_icon_data, light_image=password_icon_data, size=(17, 17))

        # Side image
        ctk.CTkLabel(master=self, text="", image=side_img).pack(expand=True, side="left")

        # Frame for login form
        frame = ctk.CTkFrame(master=self, width=400, height=480, fg_color="#ffffff")
        frame.pack_propagate(0)
        frame.pack(expand=True, side="right")

        ctk.CTkLabel(master=frame, text="Welcome Back!", text_color="#AF2B24", anchor="w", justify="left", font=("Arial Bold", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))

        ctk.CTkLabel(master=frame, text="  Username:", text_color="#AF2B24", anchor="w", justify="left", font=("Arial Bold", 14), image=email_icon, compound="left").pack(anchor="w", pady=(38, 0), padx=(25, 0))
        self.username_entry = ctk.CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#AF2B24", border_width=1, text_color="#000000")
        self.username_entry.pack(anchor="w", padx=(25, 0))

        ctk.CTkLabel(master=frame, text="  Password:", text_color="#AF2B24", anchor="w", justify="left", font=("Arial Bold", 14), image=password_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
        self.password_entry = ctk.CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#AF2B24", border_width=1, text_color="#000000", show="*")
        self.password_entry.pack(anchor="w", padx=(25, 0))

        ctk.CTkButton(master=frame, text="Login", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12), text_color="#ffffff", width=225, command=self.authenticate_user).pack(anchor="w", pady=(40, 0), padx=(25, 0))

        ctk.CTkLabel(master=frame, text="Don't have an account?", text_color="#7E7E7E", anchor="w", justify="left", font=("Arial Bold", 12)).pack(anchor="w", pady=(20, 0), padx=(27, 0))
        ctk.CTkButton(master=frame, text="Register", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12), text_color="#ffffff", width=225, command=self.show_register).pack(anchor="w", pady=(0, 0), padx=(25, 0))

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
        self.label.grid(row=0, columnspan=2, pady=12)

        self.username_label = ctk.CTkLabel(self, text="Username:")
        self.username_label.grid(row=1, column=1, padx=10, pady=10, sticky="e")
        self.username_entry = ctk.CTkEntry(self, border_color="#AF2B24")
        self.username_entry.grid(row=1, column=2, padx=10, pady=10, sticky="w")

        self.password_label = ctk.CTkLabel(self, text="Password:")
        self.password_label.grid(row=1, column=3, padx=10, pady=10, sticky="e")
        self.password_entry = ctk.CTkEntry(self, show="*", border_color="#AF2B24")
        self.password_entry.grid(row=1, column=4, padx=10, pady=10, sticky="w")

        self.email_label = ctk.CTkLabel(self, text="Email:")
        self.email_label.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        self.email_entry = ctk.CTkEntry(self, border_color="#AF2B24")
        self.email_entry.grid(row=2, column=2, padx=10, pady=10, sticky="w")

        self.first_name_label = ctk.CTkLabel(self, text="First Name:")
        self.first_name_label.grid(row=2, column=3, padx=10, pady=10, sticky="e")
        self.first_name_entry = ctk.CTkEntry(self, border_color="#AF2B24")
        self.first_name_entry.grid(row=2, column=4, padx=10, pady=10, sticky="w")

        self.last_name_label = ctk.CTkLabel(self, text="Last Name:")
        self.last_name_label.grid(row=3, column=1, padx=10, pady=10, sticky="e")
        self.last_name_entry = ctk.CTkEntry(self, border_color="#AF2B24")
        self.last_name_entry.grid(row=3, column=2, padx=10, pady=10, sticky="w")

        self.id_number_label = ctk.CTkLabel(self, text="ID Number:")
        self.id_number_label.grid(row=3, column=3, padx=10, pady=10, sticky="e")
        self.id_number_entry = ctk.CTkEntry(self, border_color="#AF2B24")
        self.id_number_entry.grid(row=3, column=4, padx=10, pady=10, sticky="w")

        self.account_type_label = ctk.CTkLabel(self, text="Account Type:")
        self.account_type_label.grid(row=4, column=1, padx=10, pady=10, sticky="e")
        self.account_type_option = ctk.CTkOptionMenu(self, fg_color="#AF2B24", values=["savings", "cheque"])
        self.account_type_option.grid(row=4, column=2, padx=10, pady=10, sticky="w")

        self.register_button = ctk.CTkButton(self, fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12), text="Register", command=self.register)
        self.register_button.grid(row=6, column=1, columnspan=4, pady=15)

        self.login_label = ctk.CTkLabel(self, text="Already have an account?")
        self.login_label.grid(row=8, column=1, columnspan=4, pady=6)
        self.login_button = ctk.CTkButton(self, fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12), text="Login", command=self.show_login)
        self.login_button.grid(row=9, column=1, columnspan=4, pady=4)

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

        self.sidebar_frame = ctk.CTkFrame(self, width=200, fg_color = "#AF2B24", corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        logo_img_data = Image.open("Untitled.png")
        logo_img = CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(77.68, 85.42))
        
        ctk.CTkLabel(self.sidebar_frame, text="", image=logo_img).pack(pady=(38, 0), anchor="center")

        dash_img_data = Image.open("Dash.png")
        dash_img = CTkImage(dark_image=dash_img_data, light_image=dash_img_data)

        self.balance_button = ctk.CTkButton(self.sidebar_frame, image = dash_img , text="Balance", fg_color="transparent", font=("Arial Bold", 14), hover_color="#FBF3E3", text_color = "black", command=self.view_balance)
        self.balance_button.pack(pady=(60, 0), ipady=5)

        transaction_img_data = Image.open("statement.png")
        transaction_img = CTkImage(dark_image = transaction_img_data, light_image = transaction_img_data)

        self.transactions_button = ctk.CTkButton(self.sidebar_frame, image = transaction_img, text="Transactions", fg_color="transparent", font=("Arial Bold", 14), hover_color="#FBF3E3", text_color = "black", command=self.view_transactions)
        self.transactions_button.pack(anchor="center", ipady=5, pady=(16, 0))

        withdraw_img_data = Image.open("withdraw.png")
        withdraw_img = CTkImage(dark_image=withdraw_img_data, light_image=withdraw_img_data)
        self.withdraw_button = ctk.CTkButton(self.sidebar_frame, text="Withdraw", image=withdraw_img, fg_color="transparent", font=("Arial Bold", 14), hover_color="#FBF3E3", text_color="black", command=self.withdraw_funds)
        self.withdraw_button.pack(anchor="center", ipady=5, pady=(16, 0))

        send_img_data = Image.open("send.png")
        send_img = CTkImage(dark_image = send_img_data, light_image = send_img_data)

        self.transfer_button = ctk.CTkButton(self.sidebar_frame, text="Money Send", image = send_img, fg_color="transparent", font=("Arial Bold", 14), hover_color="#FBF3E3", text_color = "black", command=self.transfer_funds)
        self.transfer_button.pack(anchor="center", ipady=5, pady=(16, 0))


        deposit_img_data = Image.open("deposit.png")
        deposit_img = CTkImage(dark_image = deposit_img_data, light_image = deposit_img_data)

        self.deposit_button = ctk.CTkButton(self.sidebar_frame, text="Deposit", image = deposit_img, fg_color="transparent", font=("Arial Bold", 14), hover_color="#FBF3E3", text_color = "black", command=self.deposit_funds)
        self.deposit_button.pack(anchor="center", ipady=5, pady=(16, 0))
        
        deposit_img_data = Image.open("deposit.png")
        deposit_img = CTkImage(dark_image = deposit_img_data, light_image = deposit_img_data)

        self.deposit_button = ctk.CTkButton(self.sidebar_frame, text="ChatBot", image = deposit_img, fg_color="transparent", font=("Arial Bold", 14), hover_color="#FBF3E3", text_color = "black", command=self.deposit_funds)
        self.deposit_button.pack(anchor="center", ipady=5, pady=(16, 0))

        acc_img_data = Image.open("acc.png")
        acc_img = CTkImage(dark_image=acc_img_data, light_image=acc_img_data)

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", image = acc_img, fg_color="transparent", font=("Arial Bold", 14), hover_color="#FBF3E3", text_color = "black", command=self.logout)
        self.logout_button.pack(anchor="center", ipady=5, pady=(160, 0))

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def update_user_info(self, username):
        self.username = username
        self.view_balance()

    def view_balance(self):
        self.clear_content_frame()
        users = load_users()
        balance = users[self.username]["balance"]
        balance_label = ctk.CTkLabel(self.content_frame, text=f"Current Balance: R{balance:.2f}", font=("Arial", 24))
        balance_label.pack(pady=20)

    def view_transactions(self):
        self.clear_content_frame()
        users = load_users()
        transactions = users[self.username]["transactions"]

        transactions_label = ctk.CTkLabel(self.content_frame, text="Transaction History", font=("Arial", 24))
        transactions_label.pack(pady=20)

        for transaction in transactions:
            transaction_label = ctk.CTkLabel(self.content_frame, text=transaction)
            transaction_label.pack()

    def transfer_funds(self):
        self.clear_content_frame()

        amount_label = ctk.CTkLabel(self.content_frame, text="Amount to Transfer:")
        amount_label.pack(pady=5)
        amount_entry = ctk.CTkEntry(self.content_frame, border_color="#AF2B24")
        amount_entry.pack(pady=5)

        account_label = ctk.CTkLabel(self.content_frame, text="Recipient Account Number:")
        account_label.pack(pady=5)
        account_entry = ctk.CTkEntry(self.content_frame, border_color="#AF2B24")
        account_entry.pack(pady=5)

        transfer_button = ctk.CTkButton(self.content_frame, text="Transfer", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12) , command=lambda: self.perform_transfer(amount_entry.get(), account_entry.get()))
        transfer_button.pack(pady=12)

    def perform_transfer(self, amount, account_number):
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Invalid amount.")
            return

        users = load_users()

        if account_number in [str(user["account_number"]) for user in users.values()]:
            sender = users[self.username]
            receiver = next(user for user in users.values() if str(user["account_number"]) == account_number)

            transaction_fee = calculate_transaction_fee(sender["account_type"])
            if sender["balance"] >= amount + transaction_fee:
                sender["balance"] -= (amount + transaction_fee)
                receiver["balance"] += amount

                sender_transaction = f"Transferred R{amount:.2f} to {account_number} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                receiver_transaction = f"Received R{amount:.2f} from {sender['account_number']} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                sender["transactions"].append(sender_transaction)
                receiver["transactions"].append(receiver_transaction)
                receiver["messages"].append(f"Money in: R{amount:.2f} (from {sender['account_number']})")

                save_users(users)
                messagebox.showinfo("Transfer successful!", f"Transferred R{amount:.2f} to {account_number}")
                self.view_balance()
            else:
                messagebox.showerror("Insufficient balance.")
        else:
            messagebox.showerror("Recipient account not found.")

    def deposit_funds(self):
        self.clear_content_frame()

        amount_label = ctk.CTkLabel(self.content_frame, text="Amount to Deposit:")
        amount_label.pack(pady=5)
        amount_entry = ctk.CTkEntry(self.content_frame, border_color="#AF2B24")
        amount_entry.pack(pady=5)

        deposit_button = ctk.CTkButton(self.content_frame, text="Deposit", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12), command=lambda: self.perform_deposit(amount_entry.get()))
        deposit_button.pack(pady=12)

    def perform_deposit(self, amount):
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Invalid amount.")
            return

        users = load_users()
        user = users[self.username]
        account_type = user["account_type"]
        balance = user["balance"]

        balance += amount

        transaction_fee = calculate_transaction_fee(account_type)
        balance -= transaction_fee

        users[self.username]["balance"] = balance
        transaction_record = f"Deposit of R{amount:.2f} at {datetime.now()} (Transaction Fee: R{transaction_fee:.2f})"
        users[self.username]["transactions"].append(transaction_record)
        save_users(users)

        messagebox.showinfo("Deposit successful!", f"Updated balance: R{balance:.2f}")
        self.view_balance()

    def withdraw_funds(self):
        self.clear_content_frame()

        amount_label = ctk.CTkLabel(self.content_frame, text="Amount to Withdraw:")
        amount_label.pack(pady=5)
        amount_entry = ctk.CTkEntry(self.content_frame, border_color="#AF2B24")
        amount_entry.pack(pady=5)

        withdraw_button = ctk.CTkButton(self.content_frame, text="Withdraw", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12), command=lambda: self.perform_withdrawal(amount_entry.get()))
        withdraw_button.pack(pady=12)

    def perform_withdrawal(self, amount):
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Invalid amount.")
            return

        users = load_users()
        user = users[self.username]
        balance = user["balance"]

        if balance >= amount:
            user["balance"] -= amount
            transaction_record = f"Withdrawal of R{amount:.2f} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            user["transactions"].append(transaction_record)
            save_users(users)
            messagebox.showinfo("Withdrawal successful!", f"Updated balance: R{user['balance']:.2f}")
            self.view_balance()
        else:
            messagebox.showerror("Insufficient balance.")

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = CitieBankingApp()
    app.mainloop()
