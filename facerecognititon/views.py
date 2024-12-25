import datetime
import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
import face_recognition
from PIL import Image, ImageDraw
import numpy as np
import cv2
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
import os
import cv2
import face_recognition
from django.conf import settings
from .models import Criminal
from project28 import settings
from .serializers import FileSerializer
from django.contrib.auth import logout
from .models import User, Criminal, CriminalLastSpotted

import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
import time
from threading import Timer

import smtplib


# Add this to track the last detected criminal and time of detection
last_detected_criminal = None
last_detection_time = None

email_timestamps = {}

class FileView(APIView):
  parser_classes = (MultiPartParser, FormParser)
  def post(self, request, *args, **kwargs):
    file_serializer = FileSerializer(data=request.data)
    if file_serializer.is_valid():
      file_serializer.save()
      return Response(file_serializer.data, status=status.HTTP_201_CREATED)
    else:
      return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# view for index
def index(request):
    return render(request, 'session/login.html')


#view for log in
def login(request):
    if((User.objects.filter(email=request.POST['login_email']).exists())):
        user = User.objects.filter(email=request.POST['login_email'])[0]
        if ((request.POST['login_password']== user.password)):
            request.session['id'] = user.id
            request.session['name'] = user.first_name
            request.session['surname'] = user.last_name
            messages.add_message(request,messages.INFO,'Welcome to criminal detection system '+ user.first_name+' '+user.last_name)
            return redirect(success)
        else:
            messages.error(request, 'Oops, Wrong password, please try a diffrerent one')
            return redirect('/')
    else:
        messages.error(request, 'Oops, That police ID do not exist')
        return redirect('/')


#view for log out
def logOut(request):
    logout(request)
    messages.add_message(request,messages.INFO,"Successfully logged out")
    return redirect(index)


# view to add crimina
def addCitizen(request):
   return render(request, 'home/add_citizen.html')


# view to add save citizen
def saveCitizen(request):
    if request.method == 'POST':
        citizen=Criminal.objects.filter(aadhar_no=request.POST["aadhar_no"])
        if citizen.exists():
            messages.error(request,"Citizen with that Aadhar Number already exists")
            return redirect(addCitizen)
        else:
            myfile = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            criminal = Criminal.objects.create(
                name=request.POST["name"],
                aadhar_no=request.POST["aadhar_no"],
                address=request.POST["address"],
                picture=uploaded_file_url[1:],
                status="Free"
            )
            criminal.save()
            messages.add_message(request, messages.INFO, "Citizen successfully added")
            return redirect(viewCitizens)


# view to get citizen(criminal) details
def viewCitizens(request):
    citizens=Criminal.objects.all();
    context={
        "citizens":citizens
    }
    return render(request,'home/view_citizens.html',context)


#view to set criminal status to wanted
def wantedCitizen(request, citizen_id):
    wanted = Criminal.objects.filter(pk=citizen_id).update(status='Wanted')
    if (wanted):
        messages.add_message(request,messages.INFO,"User successfully changed status to wanted")
    else:
        messages.error(request,"Failed to change the status of the citizen")
    return redirect(viewCitizens)

#view to set criminal status to free
def freeCitizen(request, citizen_id):
    free = Criminal.objects.filter(pk=citizen_id).update(status='Free')
    if (free):
        messages.add_message(request,messages.INFO,"User successfully changed status to Found and Free from Search")
    else:
        messages.error(request,"Failed to change the status of the citizen")
    return redirect(viewCitizens)


def spottedCriminals(request):
    thiefs=CriminalLastSpotted.objects.filter(status="Wanted")
    context={
        'thiefs':thiefs
    }
    return render(request,'home/spotted_thiefs.html',context)


def foundThief(request,thief_id):
    free = CriminalLastSpotted.objects.filter(pk=thief_id)
    freectzn = CriminalLastSpotted.objects.filter(aadhar_no=free.get().aadhar_no).update(status='Found')
    if(freectzn):
        thief = CriminalLastSpotted.objects.filter(pk=thief_id)
        free = Person.objects.filter(aadhar_no=thief.get().aadhar_no).update(status='Found')
        if(free):
            messages.add_message(request,messages.INFO,"Thief updated to found, congratulations")
        else:
            messages.error(request,"Failed to update thief status")
    return redirect(spottedCriminals)





def success(request):
    user = User.objects.get(id=request.session['id'])
    context = {
        "user": user
    }
    return render(request, 'home/welcome.html', context)



# View to detect and recognize faces
def detectImage(request):
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)

        # Get the criminal id, name, and images from the database
        images = []
        encodings = []
        names = []
        files = []

        prsn = Criminal.objects.filter(status="Wanted")
        for criminal in prsn:
            images.append(criminal.name + '_image')
            encodings.append(criminal.name + '_face_encoding')
            files.append(criminal.picture)
            names.append("Wanted " + criminal.name + ' ' + criminal.address)

        for i in range(0, len(images)):
            images[i] = face_recognition.load_image_file(files[i])
            encodings[i] = face_recognition.face_encodings(images[i])[0]

        # Encoding the faces of the criminals in the database 
        known_face_encodings = encodings
        known_face_names = names

        # Loading the image that is coming from the front end
        unknown_image = face_recognition.load_image_file(uploaded_file_url[1:])

        # Finding face locations and encodings of that image
        face_locations = face_recognition.face_locations(unknown_image)
        face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

        # Converting the image to PIL format
        pil_image = Image.fromarray(unknown_image)
        draw = ImageDraw.Draw(pil_image)

        # Run a loop to check if faces in the input image match those in the database
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "This is a civilian!!!"
            box_color = (0, 0, 255)  # Blue for civilians
            text_color = (255, 255, 255, 255)  # White text

            # Check for matches
            if known_face_encodings:  # Ensure there are known encodings to compare
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances) if face_distances.size > 0 else None

                if best_match_index is not None and matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    box_color = (255, 0, 0)  # Red for criminals

            # Draw a rectangle around the face
            # Ensure coordinates are correct for top, left, bottom, and right
            top, right, bottom, left = max(0, top), max(0, right), max(0, bottom), max(0, left)
            draw.rectangle(((left, top), (right, bottom)), outline=box_color, width=3)

            # Put a label below the face
            text_width, text_height = draw.textsize(name)

            # Ensure bottom text position is calculated correctly
            label_bottom = bottom + text_height + 12
            if label_bottom > pil_image.height:
                label_bottom = pil_image.height

            draw.rectangle(((left, label_bottom), (right, label_bottom + text_height)), fill=box_color)
            draw.text((left + 6, label_bottom + 0), name, fill=text_color)

        # Remove the drawing library from memory 
        del draw

        # Display the image 
        pil_image.show()
        return redirect('/success')

    return render(request, 'detect_image.html')

def detectWithWebcam(request):
    global last_detected_criminal, last_detection_time

    # Load known face encodings and names dynamically from the database
    known_face_encodings = []
    known_face_names = []

    criminals = Criminal.objects.filter(status="Wanted")

    for criminal in criminals:
        image_path = os.path.join(settings.BASE_DIR, criminal.picture)
        if os.path.exists(image_path):
            criminal_image = face_recognition.load_image_file(image_path)
            criminal_encoding = face_recognition.face_encodings(criminal_image)[0]
            known_face_encodings.append(criminal_encoding)
            known_face_names.append(criminal)
        else:
            print(f"Error: Criminal image file {image_path} not found.")

    # Initialize webcam
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print("Error: Could not access the webcam.")
        return

    print("Starting real-time criminal detection. Press 'q' to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to read from webcam.")
            break

        # Convert the frame to RGB for face recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect all face locations and encodings in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Detecting Object...."
            box_color = (255, 0, 0)  # Blue color for observing objects

            if True in matches:
                first_match_index = matches.index(True)
                criminal = known_face_names[first_match_index]
                name = criminal.name
                box_color = (0, 0, 255)  # Red color for criminals

                # If the detected criminal is the same as the last detected one
                if last_detected_criminal == criminal:
                    # If the detection happened after 3 minutes from the last detection
                    if time.time() - last_detection_time > 180:  # 180 seconds = 3 minutes
                        send_criminal_email(criminal, request.user.email, frame)
                        print(f"Email sent for {criminal.name} after 3 minutes.")
                        # Update last detection time to the current time
                        last_detection_time = time.time()
                    else:
                        print(f"Detected {criminal.name}, but email will be sent later.")
                else:
                    # New criminal detected, send email immediately
                    send_criminal_email(criminal, request.user.email, frame)
                    print(f"Email sent immediately for {criminal.name}.")
                    # Update last detection time to the current time
                    last_detection_time = time.time()

                # Update last detected criminal
                last_detected_criminal = criminal

                # Save the detected image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{criminal.name}_{criminal.address}_wanted_Zaibten_Security_{timestamp}.jpg"
                image_path = os.path.join(settings.MEDIA_ROOT, "detected_criminals", filename)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                cv2.imwrite(image_path, frame)

                # Database update (optional, if needed)
                CriminalLastSpotted.objects.filter(aadhar_no=criminal.aadhar_no).delete()
                CriminalLastSpotted.objects.create(
                    name=criminal.name,
                    aadhar_no=criminal.aadhar_no,
                    address=criminal.address,
                    picture=criminal.picture,
                    status=criminal.status,
                    latitude="25.3176° N",
                    longitude="82.9739° E",
                )
                print(f"Detected wanted criminal: {criminal.name}. Data replaced in database.")

            # Draw bounding box and label
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

        # Display the video frame with detection results
        cv2.imshow("Real-Time Criminal Detection", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    video_capture.release()
    cv2.destroyAllWindows()
    return redirect('/success')


def send_criminal_email(criminal, recipient_email, camera_frame):
    sender_email = "muzamilkhanofficial786@gmail.com"
    password = "iaqu xvna tpix ugkt"

    # HTML email body with modern UI
    subject = f"⚠️ Criminal Alert: {criminal.name} Detected"
    html_body = f"""
    <html>
        <body style="font-family: 'Arial', sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
                <header style="background-color: #343a40; padding: 20px; text-align: center;">
                    <img src="cid:logo" alt="Zaibten Security Logo" style="width: 110px; height: auto; border-radius: 50%; margin-bottom: 10px;">
                    <h1 style="color: #ffffff; font-size: 24px; margin: 0;">Zaibten Security Criminal Alert</h1>
                </header>
                <section style="padding: 20px;">
                    <h2 style="color: #333;">⚠️ Criminal Identified: {criminal.name}</h2>
                    <p style="color: #555;">The following details were recorded for the detected individual:</p>
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Name:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Address:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.address}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">CNIC No:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{criminal.aadhar_no}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Location:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">Malir Checkpost 2</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Latitude:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">25.3176° N</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; font-weight: bold;">Longitude:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">82.9739° E</td>
                        </tr>
                    </table>
                    <p style="color: #555;">Please take immediate action as required.</p>
                    <h3 style="color: #333;">Images:</h3>
                    <p style="color: #555;">1. <strong>Real-Time Detected Image (from camera):</strong></p>
                    <img src="cid:camera_image" alt="Real-Time Detected Image" style="width: 100%; height: auto; max-width: 300px; border-radius: 5px; margin-bottom: 20px;">
                    <p style="color: #555;">2. <strong>Criminal Image (from system):</strong></p>
                    <img src="cid:criminal_image" alt="Criminal Image" style="width: 100%; height: auto; max-width: 300px; border-radius: 5px; margin-bottom: 20px;">
                </section>
                <footer style="background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; color: #777;">
                    <p>© {datetime.now().year} Zaibten Security System. All rights reserved.</p>
                </footer>
            </div>
        </body>
    </html>
    """

    # Create email message
    msg = MIMEMultipart("related")
    msg['From'] = formataddr(("Criminal Detection System", sender_email))
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach HTML content
    msg.attach(MIMEText(html_body, 'html'))

    # Attach logo
    logo_path = os.path.join(os.getcwd(), "static", "assets", "images", "logo.png")
    with open(logo_path, 'rb') as f:
        logo_data = f.read()
    logo = MIMEImage(logo_data)
    logo.add_header('Content-ID', '<logo>')
    logo.add_header('Content-Disposition', 'inline', filename="logo.png")
    msg.attach(logo)

    # Attach criminal image
    criminal_image_path = os.path.join(settings.BASE_DIR, criminal.picture)
    with open(criminal_image_path, 'rb') as f:
        criminal_img_data = f.read()
    criminal_img = MIMEImage(criminal_img_data)
    criminal_img.add_header('Content-ID', '<criminal_image>')
    criminal_img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(criminal_image_path))
    msg.attach(criminal_img)

    # Attach camera image
    _, img_encoded = cv2.imencode('.jpg', camera_frame)
    img_data = img_encoded.tobytes()
    camera_img = MIMEImage(img_data)
    camera_img.add_header('Content-ID', '<camera_image>')
    camera_img.add_header('Content-Disposition', 'attachment', filename="detected_criminal.jpg")
    msg.attach(camera_img)

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email} successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

