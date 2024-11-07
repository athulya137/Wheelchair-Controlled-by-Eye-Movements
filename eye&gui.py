import tkinter as tk
import threading
import serial
import customtkinter as ctk
from PIL import Image, ImageTk
from twilio.rest import Client
import cv2
import mediapipe as mp
import pyautogui

ctk.set_appearance_mode("Dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# Set your Arduino COM port and baud rate
arduino_port = "COM5"
baud_rate = 9600

# Create serial connection to Arduino
ser = None
#ser = serial.Serial(arduino_port, baud_rate, timeout=1)

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

# Sensitivity factor (increase for higher sensitivity)
sensitivity = 10

prev_left_pupil = None
prev_right_pupil = None

def eye_control_thread():
    global prev_left_pupil, prev_right_pupil
    while True:
        _, frame = cam.read()
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks

        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark

            face_x_min = min(landmarks, key=lambda lm: lm.x).x
            face_x_max = max(landmarks, key=lambda lm: lm.x).x
            face_y_min = min(landmarks, key=lambda lm: lm.y).y
            face_y_max = max(landmarks, key=lambda lm: lm.y).y

            face_width = int((face_x_max - face_x_min) * frame_w)
            face_height = int((face_y_max - face_y_min) * frame_h)
            face_x = int(face_x_min * frame_w)
            face_y = int(face_y_min * frame_h)

            cv2.rectangle(frame, (face_x, face_y), (face_x + face_width, face_y + face_height), (0, 255, 0), 2)

            left_pupil = landmarks[468]
            right_pupil = landmarks[473]

            if prev_left_pupil is None or prev_right_pupil is None:
                prev_left_pupil = left_pupil
                prev_right_pupil = right_pupil
            else:
                left_pupil_dx = (left_pupil.x - prev_left_pupil.x) * face_width * sensitivity
                left_pupil_dy = (left_pupil.y - prev_left_pupil.y) * face_height * sensitivity
                right_pupil_dx = (right_pupil.x - prev_right_pupil.x) * face_width * sensitivity
                right_pupil_dy = (right_pupil.y - prev_right_pupil.y) * face_height * sensitivity

                x = right_pupil_dx if abs(right_pupil_dx) > abs(left_pupil_dx) else left_pupil_dx
                y = right_pupil_dy if abs(right_pupil_dy) > abs(left_pupil_dy) else left_pupil_dy

                cursor_dx = x * screen_w / face_width
                cursor_dy = y * screen_h / face_height

                pyautogui.moveRel(cursor_dx, cursor_dy)

                prev_left_pupil = left_pupil
                prev_right_pupil = right_pupil

            left_pupil_x = int((left_pupil.x - face_x_min) / (face_x_max - face_x_min) * face_width)
            left_pupil_y = int((left_pupil.y - face_y_min) / (face_y_max - face_y_min) * face_height)
            right_pupil_x = int((right_pupil.x - face_x_min) / (face_x_max - face_x_min) * face_width)
            right_pupil_y = int((right_pupil.y - face_y_min) / (face_y_max - face_y_min) * face_height)

            cv2.circle(frame, (face_x + left_pupil_x, face_y + left_pupil_y), 3, (0, 0, 255), -1)
            cv2.circle(frame, (face_x + right_pupil_x, face_y + right_pupil_y), 3, (0, 0, 255), -1)

            left_eye = [landmarks[145], landmarks[159]]
            # Check for left eye blink
            if (left_eye[0].y - left_eye[1].y) < 0.02:
                pyautogui.click()
                pyautogui.sleep(1)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        camera_label.configure(image=photo)
        camera_label.image = photo
        camera_label.after(10, lambda: None)  # Update the camera frame every 10 milliseconds

def send_command(command):
    ser.write(command.encode())

def create_button(text, command):
    return ctk.Button(root, text=text, command=lambda: send_command(command))

def on_closing():
    ser.close()
    root.destroy()

def send_whatsapp_message():
    # Your Twilio Account SID and Auth Token
    pass

def button_click():
    # send_whatsapp_message()
    pass

# GUI setup
root = ctk.CTk()
title_img = tk.PhotoImage('images/')

root.title("Arduino Wheelchair Control & Eye Tracking")
root.config(bg="#FFFFFF")
forward_photo = tk.PhotoImage(file="images/up_arrow.png")
right_photo = tk.PhotoImage(file="images/right_arrow.png")
backward_photo = tk.PhotoImage(file="images/down_arrow.png")
left_photo = tk.PhotoImage(file="images/left_arrow.png")
stop_photo = tk.PhotoImage(file="images/stop_button.png")
sos_photo = tk.PhotoImage(file="images/sos_button.png")
stop_photo = stop_photo.subsample(2, 2)
sos_photo = sos_photo.subsample(5, 5)

# Create a label to display the camera feed
camera_label = tk.Label(root)
camera_label.grid(row=1, column=3, columnspan=2, padx=5, pady=5)

# Create control buttons
forward_button = tk.Button(root, text="Forward", bg="#FFFFFF", image=forward_photo, command=lambda: send_command("U"), borderwidth=0)
backward_button = tk.Button(root, text="Backward", bg="#FFFFFF", image=backward_photo, command=lambda: send_command("D"), borderwidth=0)
stop_button = tk.Button(root, text="Stop", bg="#FFFFFF", image=stop_photo, command=lambda: send_command("S"), borderwidth=0)
left_button = tk.Button(root, text="Left", bg="#FFFFFF", image=left_photo, command=lambda: send_command("L"), borderwidth=0)
right_button = tk.Button(root, text="Right", bg="#FFFFFF", image=right_photo, command=lambda: send_command("R"), borderwidth=0)
sos_button = tk.Button(root, text="SOS", bg="#FFFFFF", image=sos_photo, command=button_click, borderwidth=0)

# Configure rows and columns to expand and fill available space
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

# Place buttons in the grid
forward_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
backward_button.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
stop_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
left_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
right_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
sos_button.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

# Close serial connection when the GUI is closed
# root.protocol("WM_DELETE_WINDOW", on_closing)

# Create a thread for the eye control process
eye_control_thread = threading.Thread(target=eye_control_thread)
eye_control_thread.daemon = True  # Daemonize the thread to automatically close it when the main thread exits

# Start the eye control thread
eye_control_thread.start()

# Start GUI main loop
root.mainloop()