 Smart Home Security System

AI-Based Real-Time Face Recognition & Access Control Prototype

 Project Overview

Smart Home Security is a real-time computer vision–based access control system developed in Python.
The system captures live video from a webcam, performs face verification using deep learning models, and determines whether the detected person is an authorized owner or a visitor.

If an unknown person is detected, the system triggers an SMS notification using third-party communication APIs.

This project demonstrates applied knowledge in:

Computer Vision

Deep Learning-based Face Verification

Real-time Video Processing

API Integration

Desktop GUI Development

 Technologies Used
Core Technologies

Python 3.x

OpenCV (cv2) – Camera access & frame processing

DeepFace – Face recognition and verification

NumPy – Numerical operations

Interface

Tkinter – Desktop graphical interface

Pillow (PIL) – Image rendering in GUI

Communication

Twilio REST API – SMS notifications

Nexmo (Vonage) – Alternative SMS service

Requests – HTTP communication

 Features

- Real-time face detection

- Owner verification

- Visitor detection

- SMS alert system

- GUI-based monitoring interface

- Date & time display


 Installation

Install dependencies
pip install opencv-python deepface numpy pillow twilio nexmo requests

 Configuration

Before running the application:

Configure your Twilio Account SID

Configure your Twilio Auth Token

(Optional) Configure Nexmo API credentials

Add authorized owner images inside the project

For security reasons, API credentials should be stored using environment variables instead of hardcoding them.

 Running the Application
python main.py

Requirements:

Connected webcam

Active internet connection (for SMS services)