import cv2
import os
import requests
from twilio.rest import Client
from deepface import DeepFace
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
from tkinter import PhotoImage
import datetime
import random
import nexmo
import pyttsx3

# Nexmo account credentials
NEXMO_API_KEY = 'xxxxxxxx'
NEXMO_API_SECRET = 'xxxxxxxxxxx'
NEXMO_BRAND_NAME = 'Verify Doorbell'

# Twilio account credentials
account_sid_1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
auth_token_1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
twilio_phone_number_1 = "+xxxxxxxxxx"
recipient_phone_number_1 = "+905xxxxxxxx"

account_sid_2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
auth_token_2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
twilio_phone_number_2 = "+xxxxxxxxx"
recipient_phone_number_2 = "+905xxxxxxxx"

client_1 = Client(account_sid_1, auth_token_1)
client_2 = Client(account_sid_2, auth_token_2)

# API key for imgbb
imgbb_api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Directory containing known faces
imageDir = 'faces'
userImages = ['your face.jpeg']  # Add other known users' images here

known_encodings = []
known_names = []

# Encode known images
for userImage in userImages:
    img_path = os.path.join(imageDir, userImage)
    if os.path.exists(img_path):
        try:
            encoding = DeepFace.represent(img_path, model_name='Facenet', enforce_detection=False)[0]['embedding']
            known_encodings.append(encoding)
            known_names.append(userImage.split('.')[0].lower())
        except Exception as e:
            print(f"Error encoding image '{userImage}': {e}")
            exit()
    else:
        print(f"Image '{userImage}' not found!")
        exit()

def get_age_range(age):
    if age < 20:
        return "(0-20)"
    elif age < 30:
        return "(20-30)"
    elif age < 40:
        return "(30-40)"
    elif age < 50:
        return "(40-50)"
    elif age < 60:
        return "(50-60)"
    else:
        return "(60+)"

def upload_image_to_imgbb(image_path):
    with open(image_path, "rb") as file:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": imgbb_api_key},
            files={"image": file}
        )
        try:
            response.raise_for_status()
            json_response = response.json()
            if 'data' in json_response and 'url' in json_response['data']:
                return json_response["data"]["url"]
            else:
                print("Unexpected JSON response format:", json_response)
                return None
        except requests.exceptions.HTTPError as err:
            print("HTTP error:", err)
            return None
        except Exception as e:
            print("Error during JSON parsing:", e)
            return None

def recognize_face(face_embedding):
    for i, known_encoding in enumerate(known_encodings):
        result = DeepFace.verify(img1_rep=face_embedding, img2_rep=known_encoding, model_name='Facenet', enforce_detection=False)
        if result["verified"]:
            return known_names[i]
    return None

def analyze_face(face_img):
    try:
        analysis_results = DeepFace.analyze(face_img, actions=['age', 'gender', 'emotion'], enforce_detection=False)[0]
        age = analysis_results["age"]
        gender = analysis_results["gender"]
        emotion = analysis_results["dominant_emotion"]
        age_range = get_age_range(age)
        return age_range, gender, emotion
    except Exception as e:
        print(f"Error in face analysis: {e}")
        return None, None, None

# Yeni şifreyi saklamak için değişken
new_password = None

def reset_and_login():
    global new_password
    new_password = simpledialog.askstring("Input", "Enter your new password:", show='*')
    if new_password:
        confirm_password = simpledialog.askstring("Input", "Confirm your new password:", show='*')
        if confirm_password == new_password:
            messagebox.showinfo("Success", "Password reset successful. Please login with your new password.")
            login()
        else:
            messagebox.showerror("Error", "Passwords do not match.")

def send_verification_code_sms(phone_number):
    client = nexmo.Client(key=NEXMO_API_KEY, secret=NEXMO_API_SECRET)
    response = client.start_verification(number=phone_number, brand=NEXMO_BRAND_NAME, code_length=4)
    if response["status"] == "0":
        print(f"Verification code SMS sent to {phone_number}.")
        return response['request_id']  # Nexmo'dan gelen doğrulama kodu için talep kimliğini döndür
    else:
        print(f"Failed to send verification code to {phone_number}. Error: {response['error_text']}")
        return None

def send_verification_code(phone_number):
    request_id = send_verification_code_sms(phone_number)
    if request_id:
        verify_code_window = tk.Toplevel(root)
        verify_code_window.title("Verification Code")
        verify_code_window.geometry("300x150")
        verify_code_window.configure(bg="#001F3F")
        lbl_verification = tk.Label(verify_code_window, text="Enter Verification Code:", font=("Helvetica", 12), bg="#001F3F", fg="white")
        lbl_verification.pack(pady=10)
        entry_verification = tk.Entry(verify_code_window, show="*")
        entry_verification.pack(pady=5)
        btn_confirm = tk.Button(verify_code_window, text="Confirm", command=lambda: check_verification_code(entry_verification.get(), request_id), font=("Helvetica", 10), bg="#ADD8E6", fg="#001F3F", relief=tk.RAISED, bd=3)
        btn_confirm.pack(pady=5)
    else:
        messagebox.showerror("Error", "Failed to send verification code. Please try again later.")

def check_verification_code(entered_code, request_id):
    client = nexmo.Client(key=NEXMO_API_KEY, secret=NEXMO_API_SECRET)
    response = client.check_verification(request_id=request_id, code=entered_code)
    if response["status"] == "0":
        messagebox.showinfo("Success", "Verification successful. You can now reset your password.")
        reset_and_login()
    else:
        messagebox.showerror("Error", "Incorrect verification code. Please try again.")

        
def forgot_password():
    username = simpledialog.askstring("Input", "Enter your username:")
    if username.lower() == "your username": # Değiştirilecek: Gerçek kullanıcı adıyla karşılaştırma yapılmalı
        phone_number = simpledialog.askstring("Input", "Enter your phone number (in format +90XXXXXXXXXX):")
        send_verification_code(phone_number)
    else:
        messagebox.showerror("Error", "Invalid username.")
        
def login():
    username = simpledialog.askstring("Input", "Enter your username:")
    if username.lower() == "your username": # Değiştirilecek: Gerçek kullanıcı adıyla karşılaştırma yapılmalı
        password = simpledialog.askstring("Input", "Enter your password:", show='*')
        if password == "your password": # Değiştirilecek: Gerçek şifreyle karşılaştırma yapılmalı
            messagebox.showinfo("Success", "Welcome!")
            # Owner login success, update UI
            owner_frame.configure(bg="#5BC0EB")
            owner_label.configure(fg="#001F3F")
            btn_owner.configure(bg="#70C1B3", fg="#001F3F")
        else:
            messagebox.showerror("Error", "Incorrect password.")
    else:
        messagebox.showerror("Error", "Invalid username.")


def open_camera():
    # Hoş geldiniz mesajını sesli olarak söyle
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say("Welcome, please refer to the camera for facial recognition.")
    engine.runAndWait()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    success, img = cap.read()
    if success:
        img = cv2.flip(img, 1)
        recognized_names = []
        unknown_people_info = []
        sms_body = ""


        try:
            detected_faces = DeepFace.extract_faces(img, detector_backend='opencv', enforce_detection=False)
            if detected_faces:
                for face in detected_faces:
                    face_img = face['face']
                    face_embedding = DeepFace.represent(face_img, model_name='Facenet', enforce_detection=False)[0]['embedding']
                    
                    recognized_name = recognize_face(face_embedding)
                    if recognized_name:
                        recognized_names.append(recognized_name)
                    else:
                        age_range, gender, emotion = analyze_face(face_img)
                        if age_range and gender and emotion:
                            unknown_people_info.append(f"Age Range: {age_range}, Gender: {gender}, Dominant Emotion: {emotion}")

                            face_path = "temp_face.jpg"
                            cv2.imwrite(face_path, face_img)
                            img_url = upload_image_to_imgbb(face_path)
                            unknown_people_info[-1] += f". Photo: {img_url}"

            else:
                print("No faces detected.")
        except Exception as e:
            print(f"Error in face verification: {e}")

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if recognized_names:
            recognized_names_str = ', '.join([name.capitalize() for name in recognized_names])
            sms_body = f"{recognized_names_str} is/are at the door"
            if unknown_people_info:
                sms_body += f" and {len(unknown_people_info)} unknown person(s): " + "; ".join(unknown_people_info)
        else:
            img_path = "unknown_visitor.jpg"
            cv2.imwrite(img_path, img)
            age_range, gender, emotion = analyze_face(img)
            if age_range and gender and emotion:
                sms_body = f"Unknown person detected at the door: Age Range: {age_range}, Gender: {gender}, Dominant Emotion: {emotion}"

            img_url = upload_image_to_imgbb(img_path)
            sms_body += f". Photo: {img_url}"

            message_1 = client_1.messages.create(
                body=sms_body,
                from_=twilio_phone_number_1,
                to=recipient_phone_number_1,
                media_url=[img_url]
            )
            print("SMS sent to recipient 1:", message_1.sid)
            
            message_2 = client_2.messages.create(
                body=sms_body,
                from_=twilio_phone_number_2,
                to=recipient_phone_number_2,
                media_url=[img_url]
            )
            print("SMS sent to recipient 2:", message_2.sid)
        
        if recognized_names:
            message_1 = client_1.messages.create(
                body=f"{current_time}: {sms_body}",
                from_=twilio_phone_number_1,
                to=recipient_phone_number_1
            )
            print(f"SMS sent to recipient 1 at {current_time}: {message_1.sid}")
            message_2 = client_2.messages.create(
                body=f"{current_time}: {sms_body}",
                from_=twilio_phone_number_2,
                to=recipient_phone_number_2
            )
            print(f"SMS sent to recipient 2 at {current_time}: {message_2.sid}")
        else:
            message_1 = client_1.messages.create(
                body=f"{current_time}: {sms_body}",
                from_=twilio_phone_number_1,
                to=recipient_phone_number_1
            )
            print(f"SMS sent to recipient 1 at {current_time}: {message_1.sid}")
            message_2 = client_2.messages.create(
                body=f"{current_time}: {sms_body}",
                from_=twilio_phone_number_1,
                to=recipient_phone_number_2
            )
            print(f"SMS sent to recipient 2 at {current_time}: {message_2.sid}")
           
    else:
        print("Failed to capture image from camera.")

    cap.release()
    cv2.destroyAllWindows()

root = tk.Tk()
root.title("Security Doorbell Application")
root.geometry("600x400")
root.configure(bg="#001F3F")

# Frame Creation
title_frame = tk.Frame(root, bg="#001F3F")
title_frame.pack(anchor=tk.W, padx=10, pady=10)

# Placing Text on Frame
title_label = tk.Label(title_frame, text="Smart Home Security", font=("Montserrat", 28, "bold"), bg="#001F3F", fg="white")
title_label.pack(anchor=tk.W, padx=10, pady=(20, 10))

# Loading Icons
visitor_icon = PhotoImage(file="visitor_icon.png").subsample(2)
owner_icon = PhotoImage(file="owner_icon.png").subsample(2)

# Visitor and Owner Frames
visitor_frame = tk.Frame(root, bg="#001F3F")
visitor_frame.pack(side=tk.LEFT, padx=20)

owner_frame = tk.Frame(root, bg="#001F3F")
owner_frame.pack(side=tk.LEFT, padx=20)

# Visitor
visitor_label = tk.Label(visitor_frame, image=visitor_icon, bg="#001F3F")
visitor_label.grid(row=0, column=0)

btn_visitor = tk.Button(visitor_frame, text="Visitor", font=("Helvetica", 12, "bold"), command=open_camera, bg="#ADD8E6", fg="#001F3F", relief=tk.RAISED, bd=3)
btn_visitor.grid(row=1, column=0, pady=25)

# Owner
owner_label = tk.Label(owner_frame, image=owner_icon, bg="#001F3F")
owner_label.grid(row=0, column=0)

btn_owner = tk.Button(owner_frame, text="Owner Login", font=("Helvetica", 12, "bold"), command=login, bg="#ADD8E6", fg="#001F3F", relief=tk.RAISED, bd=3)
btn_owner.grid(row=1, column=0, pady=3)

# Add a space between the Owner Login button and the Forgot Password button
tk.Label(owner_frame, text="", bg="#001F3F").grid(row=2, column=0)

# Forgot Password
btn_forgot_password = tk.Button(owner_frame, text="Forgot Password", font=("Helvetica", 12, "bold"), command=forgot_password, bg="#ADD8E6", fg="#001F3F", relief=tk.RAISED, bd=3)
btn_forgot_password.grid(row=2, column=0, pady=3)

# Date and Time
date_time_frame = tk.Frame(root, bg="#001F3F")
date_time_frame.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

date_icon_label = tk.Label(date_time_frame, bg="#001F3F")
date_icon_label.grid(row=0, column=0, padx=2)
date_label = tk.Label(date_time_frame, text=datetime.datetime.now().strftime("%Y-%m-%d"), font=("Helvetica", 12), bg="#001F3F", fg="white", padx=2)
date_label.grid(row=1, column=0, padx=2)

clock_icon_label = tk.Label(date_time_frame, bg="#001F3F")
clock_icon_label.grid(row=0, column=1, padx=2)
clock_label = tk.Label(date_time_frame, text=datetime.datetime.now().strftime("%H:%M:%S"), font=("Helvetica", 12), bg="#001F3F", fg="white", padx=2)
clock_label.grid(row=1, column=1, padx=2)

def update_clock():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    clock_label.config(text=current_time)
    root.after(1000, update_clock)

def update_date():
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    date_label.config(text=current_date)
    root.after(86400000, update_date)  # 86400000 ms = 24 hours

update_clock()
update_date()

root.mainloop()