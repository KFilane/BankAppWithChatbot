import os
import json
import re
import random
from datetime import datetime
from tkinter import messagebox
from email.mime import image
import bcrypt
from PIL import Image
import customtkinter as ctk
from customtkinter import CTkImage, set_default_color_theme

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
        if not any(user.get('account_number') == account_number for user in users.values()):
            return account_number

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def determine_gender(id_number):
    return "female" if int(id_number[6]) % 2 == 0 else "male"

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
        self.username = None

        self.login_frame = LoginFrame(self, self.show_register_frame, self.login_success)
        self.register_frame = RegisterFrame(self, self.show_login_frame, self.register_user)
        self.dashboard_frame = DashboardFrame(self, self.logout)

        self.login_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        self.geometry("1024x768")
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
        side_img = self.load_image("Untitled.png", size=(400, 480))
        email_icon = self.load_image("uname.png", size=(20, 20))
        password_icon = self.load_image("lcok.png", size=(17, 17))

        # Side image
        ctk.CTkLabel(master=self, text="", image=side_img).pack(expand=True, side="left")

        # Frame for login form
        frame = ctk.CTkFrame(master=self, width=400, height=480, fg_color="#ffffff")
        frame.pack_propagate(0)
        frame.pack(expand=True, side="right")

        self.create_label(frame, "Welcome Back!", 24, pady=(50, 5))
        self.create_label(frame, "  Username:", 14, image=email_icon, pady=(38, 0))
        self.username_entry = self.create_entry(frame, show=None)

        self.create_label(frame, "  Password:", 14, image=password_icon, pady=(21, 0))
        self.password_entry = self.create_entry(frame, show="*")

        ctk.CTkButton(master=frame, text="Login", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12),
                      text_color="#ffffff", width=225, command=self.authenticate_user).pack(anchor="w", pady=(40, 0), padx=(25, 0))

        self.create_label(frame, "Don't have an account?", 12, text_color="#7E7E7E", pady=(20, 0))
        ctk.CTkButton(master=frame, text="Register", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12),
                      text_color="#ffffff", width=225, command=self.show_register).pack(anchor="w", pady=(0, 0), padx=(25, 0))

    def load_image(self, filepath, size):
        img_data = Image.open(filepath)
        return ctk.CTkImage(dark_image=img_data, light_image=img_data, size=size)

    def create_label(self, parent, text, font_size, text_color="#AF2B24", image=None, pady=(0, 0), padx=(25, 0)):
        label = ctk.CTkLabel(master=parent, text=text, text_color=text_color, anchor="w", justify="left",
                             font=("Arial Bold", font_size), image=image, compound="left")
        label.pack(anchor="w", pady=pady, padx=padx)
        return label

    def create_entry(self, parent, show):
        entry = ctk.CTkEntry(master=parent, width=225, fg_color="#EEEEEE", border_color="#AF2B24", border_width=1,
                             text_color="#000000", show=show)
        entry.pack(anchor="w", padx=(25, 0))
        return entry

    def authenticate_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        users = load_users()
        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]["password"].encode('utf-8')):
            if not users[username].get("maintenance_fee_deducted", False):
                self.deduct_maintenance_fee(users, username)
            self.login_success(username)
        else:
            messagebox.showerror("Invalid username or password")

    def deduct_maintenance_fee(self, users, username):
        user = users[username]
        account_type = user["account_type"]
        maintenance_fee = calculate_maintenance_fee(account_type)
        user["balance"] -= maintenance_fee
        user["maintenance_fee_deducted"] = True
        transaction_record = f"Maintenance fee of R{maintenance_fee:.2f} deducted at {datetime.now()}"
        user["transactions"].append(transaction_record)
        save_users(users)
        messagebox.showinfo("Maintenance fee", f"Maintenance fee of R{maintenance_fee:.2f} has been deducted from your account.")

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, show_login, register_user):
        super().__init__(parent)
        self.show_login = show_login
        self.register_user = register_user

        self.create_form()

    def create_form(self):
        self.create_label("Register", 24, row=0, col_span=2, pady=12)

        self.username_entry = self.create_input_row("Username:", 1, 1)
        self.password_entry = self.create_input_row("Password:", 1, 3, show="*")
        self.email_entry = self.create_input_row("Email:", 2, 1)
        self.first_name_entry = self.create_input_row("First Name:", 2, 3)
        self.last_name_entry = self.create_input_row("Last Name:", 3, 1)
        self.id_number_entry = self.create_input_row("ID Number:", 3, 3)
        self.account_type_option = self.create_option_menu("Account Type:", ["savings", "cheque"], 4, 1)

        self.create_button("Register", self.register, row=6, col_span=4, pady=15)
        self.create_label("Already have an account?", 12, row=8, col_span=4, pady=6)
        self.create_button("Login", self.show_login, row=9, col_span=4, pady=4)

    def create_label(self, text, font_size, row, col_span=1, pady=0):
        label = ctk.CTkLabel(master=self, text=text, font=("Arial Bold", font_size))
        label.grid(row=row, columnspan=col_span, pady=pady)
        return label

    def create_input_row(self, label_text, row, col, show=None):
        self.create_label(label_text, 14, row=row, col_span=1, pady=4)
        entry = ctk.CTkEntry(master=self, width=200, show=show)
        entry.grid(row=row, column=col, pady=4, padx=10)
        return entry

    def create_option_menu(self, label_text, options, row, col):
        self.create_label(label_text, 14, row=row, col_span=1, pady=4)
        option_menu = ctk.CTkOptionMenu(master=self, values=options)
        option_menu.grid(row=row, column=col, pady=4, padx=10)
        return option_menu

    def create_button(self, text, command, row, col_span=1, pady=0):
        button = ctk.CTkButton(master=self, text=text, command=command)
        button.grid(row=row, columnspan=col_span, pady=pady)
        return button

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        id_number = self.id_number_entry.get().strip()
        account_type = self.account_type_option.get().strip()

        if not username or not password or not email or not first_name or not last_name or not id_number or not account_type:
            messagebox.showerror("Error", "All fields are required")
            return

        if not is_valid_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return

        users = load_users()
        if username in users:
            messagebox.showerror("Error", "Username already exists")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        gender = determine_gender(id_number)
        account_number = generate_account_number(users)
        balance = 100.0  # Initial balance
        transactions = []

        new_user = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "id_number": id_number,
            "gender": gender,
            "account_type": account_type,
            "account_number": account_number,
            "balance": balance,
            "transactions": transactions,
            "maintenance_fee_deducted": False
        }

        self.register_user(new_user)

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, logout):
        super().__init__(parent)
        self.logout = logout

    def update_user_info(self, username):
        users = load_users()
        user = users.get(username, {})

        for widget in self.winfo_children():
            widget.destroy()

        self.create_label(f"Welcome!, {user.get('first_name', '')} {user.get('last_name', '')}", 20, pady=(10, 5))
        self.create_label(f"Account Number: {user.get('account_number', '')}", 16, pady=(5, 5))
        self.create_label(f"Account Type: {user.get('account_type', '')}", 16, pady=(5, 5))
        self.create_label(f"Balance: R{user.get('balance', 0.0):.2f}", 16, pady=(5, 5))

        self.create_button("Logout", self.logout, pady=(20, 0))

    def create_label(self, text, font_size, pady=0):
        label = ctk.CTkLabel(master=self, text=text, font=("Arial Bold", font_size))
        label.pack(pady=pady)
        return label

    def create_button(self, text, command, pady=0):
        button = ctk.CTkButton(master=self, text=text, command=command)
        button.pack(pady=pady)
        return button

if __name__ == "__main__":
    app = CitieBankingApp()
    app.mainloop()
