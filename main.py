from customtkinter import *
import customtkinter
from PIL import Image

app = CTk()
app.geometry("1024×768")
app.resizable(0,0)

customtkinter.set_appearance_mode("dark")  

side_img_data = Image.open("Untitled.png")
email_icon_data = Image.open("email_envelop.png")
password_icon_data = Image.open("lcok.png")
google_icon_data = Image.open("acc.png")

side_img = CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(350, 480))
email_icon = CTkImage(dark_image=email_icon_data, light_image=email_icon_data, size=(20,20))
password_icon = CTkImage(dark_image=password_icon_data, light_image=password_icon_data, size=(17,17))
google_icon = CTkImage(dark_image=google_icon_data, light_image=google_icon_data, size=(17,17))

CTkLabel(master=app, text="", image=side_img).pack(expand=True, side="left")

frame = CTkFrame(master=app, width=350, height=480, fg_color="#ffffff")
frame.pack_propagate(0)
frame.pack(expand=True, side="right")

CTkLabel(master=frame, text="Welcome Back!", text_color="#AF2B24", anchor="w", justify="left", font=("Arial Bold", 24)).pack(anchor="w", pady=(50, 5), padx=(25, 0))

CTkLabel(master=frame, text="  Email:", text_color="#AF2B24", anchor="w", justify="left", font=("Arial Bold", 14), image=email_icon, compound="left").pack(anchor="w", pady=(38, 0), padx=(25, 0))
CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#AF2B24", border_width=1, text_color="#000000").pack(anchor="w", padx=(25, 0))

CTkLabel(master=frame, text="  Password:", text_color="#AF2B24", anchor="w", justify="left", font=("Arial Bold", 14), image=password_icon, compound="left").pack(anchor="w", pady=(21, 0), padx=(25, 0))
CTkEntry(master=frame, width=225, fg_color="#EEEEEE", border_color="#AF2B24", border_width=1, text_color="#000000", show="*").pack(anchor="w", padx=(25, 0))

CTkButton(master=frame, text="Login", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12), text_color="#ffffff", width=225).pack(anchor="w", pady=(40, 0), padx=(25, 0))

CTkLabel(master=frame, text="Don't have an account?", text_color="#7E7E7E", anchor="w", justify="left", font=("Arial Bold", 12)).pack(anchor="w", pady=(20, 0), padx=(27, 0))
CTkButton(master=frame, text="Register", fg_color="#AF2B24", hover_color="#F7A425", font=("Arial Bold", 12), text_color="#ffffff", width=225).pack(anchor="w", pady=(0, 0), padx=(25, 0))


app.mainloop()