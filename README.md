# 🌐 Criminal Detection Web App Using Python Django 👮‍♂️
Zaibten Security is a robust web application designed to identify criminals by leveraging their stored images and live webcam footage. It integrates modern technologies like face recognition, computer vision, and real-time video streaming to enable efficient and accurate detection of known criminals.

# 🚔 Empowering Law Enforcement with Technology
Introducing my latest innovation: a Criminal Detection Web Application built with Python Django! This platform integrates real-time criminal detection, video analysis, and a robust admin panel to provide a seamless and effective solution for modern law enforcement.

# Core Features
1. 🎥 Real-Time Detection: Processes live camera feeds to identify suspects instantly.
2. 📸 Video and Image Analysis: Upload videos or images for retrospective detection and analysis.
3. 📍 Location Tracking: Automatically pinpoints the location of identified criminals using Google Maps API.
4. 📧 SMTP Notifications: Sends immediate email alerts to authorities when a match is detected.
5. 🔐 Admin Dashboard: Manage criminal profiles, track incidents, and generate detailed reports.

# Technical Overview
# 1️⃣ Backend:
1. Built with Django for scalable and secure operations.
2. Integrated TensorFlow models for facial recognition and image processing.

# 2️⃣ Frontend:
1. Intuitive interface for camera feeds, file uploads, and analysis results.
2. Admin panel for data management and incident tracking.

# 3️⃣ Real-Time Detection:
1. Used OpenCV for live video feed processing.
2. Models deployed for real-time prediction and identification.

# 4️⃣ Additional Features:
1. SMTP Service: Configured to send email alerts to stakeholders with crime details and suspect images.
2. Google Maps Integration: Displays precise locations where suspects are detected.
3. Use Case Scenarios
4. Surveillance in Public Areas: Track criminal activities in crowded places like stations and malls.
5. Law Enforcement Alerts: Real-time notifications for quicker responses.
6. Criminal Records Management: Maintain profiles of suspects for future reference.

# Why This Project Matters?
In an era where safety is paramount, this project provides a holistic solution to modern security challenges. By combining the power of AI, web technologies, and real-time processing, it aims to make the world a safer place.

## How to run the application
### Installation requirements
First of all, clone the git hub repository on your machine.  
Make sure you have python downloaded, incase you haven't already visit this link: https://www.python.org/downloads/  

To install the required packages use the following command

```bash
 pip install -r requirements.txt
```

In settings.py file change the variable DATABASES:

```bash
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/path/to/my.cnf',
        },
    }
}

# my.cnf
[client]
database = NAME
user = USER
password = PASSWORD
default-character-set = utf8
```

Apply migrations
```bash
 python manage.py makemigrations
 python manage.py migrate
```

To start the app
```bash
 python manage.py runserver
```
And run on localhost at your system

```bash
And open http://127.0.0.1:8000/
```
### 🔗 Let’s innovate together! If you’re interested in collaborating or have feedback, I’d love to hear from you. 😊

# 💡 Join the conversation:
What features would you like to see in a real-time criminal detection system? Let’s discuss how we can make security smarter and more efficient. 🚀

# 📸 Some Screenshots of the Project 🖼️✨
![image](https://github.com/user-attachments/assets/72cfe69f-2225-4d14-b6ac-af8ae979aa49)
![image](https://github.com/user-attachments/assets/739a8c15-a4c0-4c60-8825-9889933d107c)
![image](https://github.com/user-attachments/assets/0eddb973-8026-40ad-a483-871311746adf)
![image](https://github.com/user-attachments/assets/e704fbcf-9b81-403c-9bae-75e512adff70)
![image](https://github.com/user-attachments/assets/97e3831b-0289-47d6-9da9-9ea80c4aa700)
![image](https://github.com/user-attachments/assets/7fb11e65-ff7b-4930-b6c5-35bbd9d946fb)
![image](https://github.com/user-attachments/assets/a3588e42-6043-430f-befc-20ac36d17c7d)
![image](https://github.com/user-attachments/assets/08bf45e2-3402-4168-9677-0eb3b585474c)
![image](https://github.com/user-attachments/assets/764d0697-85d2-40bd-a449-39dab7e8824f)
![image](https://github.com/user-attachments/assets/b8942ff6-0c52-4743-b002-280b897a9387)

















