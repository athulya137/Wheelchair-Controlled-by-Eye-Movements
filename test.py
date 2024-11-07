import tkinter as tk
import serial
import customtkinter as ctk
from PIL import Image,ImageTk
from twilio.rest import Client

ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# Set your Arduino COM port and baud rate
arduino_port = "COM5"
baud_rate = 9600

# Create serial connection to Arduino
ser=None
#ser = serial.Serial(arduino_port, baud_rate, timeout=1)


def send_command(command):
    ser.write(command.encode())


def create_button(text, command):
    return ctk.Button(root, text=text, command=lambda: send_command(command))

def on_closing():
    ser.close()
    root.destroy()


def send_whatsapp_message():
    # Your Twilio Account SID and Auth Token
    account_sid = 'ACfd6d9ae1158c9a9184070e462e8c69c8'
    auth_token = 'ae4c537a4661f3f6d025999d0943a117'

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    # Send a message to WhatsApp
    message = client.messages.create(
        body='Wheelchair in trouble',
        from_='whatsapp:+14155238886',
        to='whatsapp:+919061135981'
    )

    print("Message sent successfully:", message.sid)

def button_click():
    send_whatsapp_message()

# GUI setup
root =ctk.CTk()
title_img = tk.PhotoImage('images/')

root.title("Arduino Wheelchair Control")
root.config(bg="#FFFFFF")
forward_photo=tk.PhotoImage(file="images/up_arrow.png")
right_photo=tk.PhotoImage(file="images/right_arrow.png")
backward_photo=tk.PhotoImage(file="images/down_arrow.png")
left_photo=tk.PhotoImage(file="images/left_arrow.png")
stop_photo=tk.PhotoImage(file="images/stop_button.png")
sos_photo=tk.PhotoImage(file="images/sos_button.png")
stop_photo=stop_photo.subsample(2,2)
sos_photo=sos_photo.subsample(3,3)

# Create control buttons
forward_button = tk.Button(root,text="Forward",bg="#FFFFFF",image=forward_photo,command=lambda:send_command("U"),borderwidth=0)
backward_button = tk.Button(root,text="Backward",bg="#FFFFFF",image=backward_photo,command=lambda:send_command("D"),borderwidth=0)
stop_button = tk.Button(root,text="Stop",bg="#FFFFFF",image=stop_photo,command=lambda:send_command("S"),borderwidth=0)
left_button = tk.Button(root,text="Left",bg="#FFFFFF",image=left_photo,command=lambda:send_command("L"),borderwidth=0)
right_button = tk.Button(root,text="Right",bg="#FFFFFF",image=right_photo,command=lambda:send_command("R"),borderwidth=0)
sos_button = tk.Button(root,text="SOS",bg="#FFFFFF",image=sos_photo,command=button_click,borderwidth=0)

# Configure rows and columns to expand and fill available space
root.rowconfigure(0,weight=1 )
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1 )
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

# Place buttons in the grid
forward_button.grid(row=0, column=1,padx=10, pady=10, sticky="nsew")
backward_button.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
stop_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
left_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
right_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
sos_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")


# Close serial connection when the GUI is closed
root.protocol("WM_DELETE_WINDOW", on_closing)


# Start GUI main loop
root.mainloop()
