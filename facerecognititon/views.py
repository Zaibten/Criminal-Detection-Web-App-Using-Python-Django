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


# view to detect and recognise faces
# def detectImage(request):
#     # function to detect faces and draw a rectangle around the faces
#     # with correct face label

#     if request.method == 'POST' and request.FILES['image']:
#         myfile = request.FILES['image']
#         fs = FileSystemStorage()
#         filename = fs.save(myfile.name, myfile)
#         uploaded_file_url = fs.url(filename)

#     # get the criminal id, name, images from the database
#     images=[]
#     encodings=[]
#     names=[]
#     files=[]

#     prsn=Criminal.objects.all()
#     for criminal in prsn:
#         images.append(criminal.name+'_image')
#         encodings.append(criminal.name+'_face_encoding')
#         files.append(criminal.picture)
#         names.append(criminal.name+ ' '+ criminal.address)

    
#     for i in range(0,len(images)):
#         images[i]=face_recognition.load_image_file(files[i])
#         encodings[i]=face_recognition.face_encodings(images[i])[0]




#     # encoding the faces of the criminals in the database 
#     # creating array of their names
#     known_face_encodings = encodings
#     known_face_names = names

#     # loading the image that is coming from the front end
#     unknown_image = face_recognition.load_image_file(uploaded_file_url[1:])

#     # finding face locations and encoding of that image
#     face_locations = face_recognition.face_locations(unknown_image)
#     face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

#     # converting the image to PIL format
#     pil_image = Image.fromarray(unknown_image)
#     #Draw a rectangle over the face
#     draw = ImageDraw.Draw(pil_image)

#     # run a for loop to find if faces in the input image matches to that 
#     # of our encoding present in the DB
#     for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#         # compare the face to the criminals present
#         matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#         name = "This is civilian not criminal!!!"

#         # find distance w.r.t to the faces of criminals present in the DB
#         # take the minimum distance
#         # see if it matches the faces
#         # if matches update the name variable to the respective criminal name
#         face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
#         best_match_index = np.argmin(face_distances)
#         if matches[best_match_index]:
#             name = known_face_names[best_match_index]


#         # with pollow module draw a rectangle around the face
#         # draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
#         draw.rectangle(((left, top), (right, bottom)), outline=(255, 0, 0))  # Red color
        
#         text_width, text_height = draw.textsize(name)
#         draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(255, 0, 0), outline=(255, 0, 0))  # Red color
#         draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))  # White text

#         # put a label of name of the person below
#         # text_width, text_height = draw.textsize(name)
#         # draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
#         # draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

#     # Remove the drawing library from memory 
#     del draw

#     # display the image 
#     pil_image.show()
#     return redirect('/success')

# def detectWithWebcam(request):
#     # Load known face encodings and names
#     known_face_encodings = []
#     known_face_names = []

#     # Define the image path using BASE_DIR
#     image_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'card', '8.jpg')
    
#     # Load known face and names
#     try:
#         known_personal_image = face_recognition.load_image_file(image_path)
#         known_face_person_encoding = face_recognition.face_encodings(known_personal_image)[0]

#         known_face_encodings.append(known_face_person_encoding)
#         known_face_names.append("Criminal")

#     except FileNotFoundError:
#         print(f"Error: The image file at {image_path} was not found.")
#         # Handle the error appropriately (e.g., return an error message)

#     # Initialize Webcam
#     video_capture = cv2.VideoCapture(0)

#     while True:
#         # Capture frame-by-frame
#         ret, frame = video_capture.read()
#         if not ret:
#             break

#         # Convert the frame from BGR to RGB
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Find all face locations and face encodings in the current video frame
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through each face found in the frame
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # Check if the face matches any known faces
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Civilian"
#             box_color = (0, 255, 0)  # Green for Civilian

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]
#                 box_color = (0, 0, 255)  # Red for Criminal

#             # Draw a box around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)

#             # Draw a label with a name below the face
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)

#         # Display the resulting frame
#         cv2.imshow("Video", frame)

#         # Break the loop when the "q" key is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release the webcam and close OpenCV windows
#     video_capture.release()
#     cv2.destroyAllWindows()

# def detectWithWebcam(request):
#     # Access the default camera
#     video_capture = cv2.VideoCapture(0)

#     # Loading faces and data from the database
#     known_face_encodings = []
#     known_face_names = []
#     national_ids = []

#     criminals = Criminal.objects.all()

#     # Load criminal data
#     for criminal in criminals:
#         image_path = criminal.picture.path  # Assuming the 'picture' field stores the file path
#         image = face_recognition.load_image_file(image_path)
#         encoding = face_recognition.face_encodings(image)

#         if encoding:
#             known_face_encodings.append(encoding[0])  # Save only the first encoding in case there are multiple
#             known_face_names.append(f"Name: {criminal.name}, Aadhar: {criminal.aadhar_no}, Address: {criminal.address}")
#             national_ids.append(criminal.aadhar_no)

#     while True:
#         # Capture frame-by-frame
#         ret, frame = video_capture.read()
#         if not ret:
#             break

#         # Convert the frame from BGR to RGB for face recognition
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Find all face locations and encodings in the current video frame
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Process each face found in the frame
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # Check if the face matches any known faces
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

#             name = "Unknown"  # Default name for unknown faces
#             box_color = (0, 255, 0)  # Green for unknown faces

#             if matches:
#                 # Get the best match (the face with the smallest distance)
#                 best_match_index = np.argmin(face_distances)
#                 if matches[best_match_index]:
#                     # Match found, retrieve the details
#                     ntnl_id = national_ids[best_match_index]
#                     criminal = Criminal.objects.get(aadhar_no=ntnl_id)
#                     name = f"{known_face_names[best_match_index]}, Status: {criminal.status}"
#                     box_color = (0, 0, 255)  # Red for wanted criminals

#                     # Add to CriminalLastSpotted if the criminal is wanted
#                     if criminal.status == 'Wanted':
#                         CriminalLastSpotted.objects.create(
#                             name=criminal.name,
#                             aadhar_no=criminal.aadhar_no,
#                             address=criminal.address,
#                             picture=criminal.picture,
#                             status='Wanted',
#                             latitude='25.3176° N',  # You can dynamically get GPS data here
#                             longitude='82.9739° E'  # You can dynamically get GPS data here
#                         )

#             # Draw a rectangle around the face and add name label
#             cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)

#         # Display the resulting frame
#         cv2.imshow("Video", frame)

#         # Break the loop when 'q' is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release the webcam and close OpenCV windows
#     video_capture.release()
#     cv2.destroyAllWindows()

#     return redirect('/success')

# def detectWithWebcam(request):
#     # Load known face encodings and names dynamically from the database
#     known_face_encodings = []
#     known_face_names = []

#     criminals = Criminal.objects.all()
#     for criminal in criminals:
#         # Assuming picture is a relative path stored in the database
#         image_path = os.path.join(settings.BASE_DIR, criminal.picture)
#         if os.path.exists(image_path):
#             criminal_image = face_recognition.load_image_file(image_path)
#             criminal_encoding = face_recognition.face_encodings(criminal_image)[0]
#             known_face_encodings.append(criminal_encoding)
#             known_face_names.append(f"Name: {criminal.name}, CNIC: {criminal.aadhar_no}, Address: {criminal.address}, Criminal Detected")
#         else:
#             print(f"Error: Criminal image file {image_path} not found.")

#     # Initialize webcam
#     video_capture = cv2.VideoCapture(0)
#     if not video_capture.isOpened():
#         print("Error: Could not access webcam.")
#         return

#     while True:
#         # Capture frame-by-frame
#         ret, frame = video_capture.read()
#         if not ret:
#             print("Error: Failed to read from webcam.")
#             break

#         # Convert frame from BGR to RGB for face recognition
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Detect faces and compute encodings
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         # Loop through detected faces
#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # Compare detected face encodings with known faces
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Civilian"
#             box_color = (0, 255, 0)  # Green for Civilian

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]
#                 box_color = (0, 0, 255)  # Red for Criminal

#             # Draw a rectangle around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
#             # Label the detected face
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)

#         # Display the resulting frame
#         cv2.imshow("Criminal Detection", frame)

#         # Exit on 'q' key press
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release resources
#     video_capture.release()
#     cv2.destroyAllWindows()

# def detectWithWebcam(request):
#     # Load known face encodings and names dynamically from the database
#     known_face_encodings = []
#     known_face_names = []

#     criminals = Criminal.objects.all()
#     for criminal in criminals:
#         image_path = os.path.join(settings.BASE_DIR, criminal.picture)
#         if os.path.exists(image_path):
#             criminal_image = face_recognition.load_image_file(image_path)
#             criminal_encoding = face_recognition.face_encodings(criminal_image)[0]
#             known_face_encodings.append(criminal_encoding)
#             known_face_names.append(f"Name: {criminal.name}, Aadhar: {criminal.aadhar_no}, Address: {criminal.address}")
#         else:
#             print(f"Error: Criminal image file {image_path} not found.")

#     # Initialize webcam
#     video_capture = cv2.VideoCapture(0)
#     if not video_capture.isOpened():
#         print("Error: Could not access webcam.")
#         return

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             print("Error: Failed to read from webcam.")
#             break

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Civilian"
#             box_color = (0, 255, 0)  # Green for Civilian

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 criminal = Criminal.objects.get(name=known_face_names[first_match_index].split(",")[0].split(":")[1].strip())
#                 name = known_face_names[first_match_index]
#                 box_color = (0, 0, 255)  # Red for Criminal

#                 # Check if the criminal is wanted
#                 if criminal.status.lower() == 'Wanted':
#                     CriminalLastSpotted.objects.create(
#                         name=criminal.name,
#                         aadhar_no=criminal.aadhar_no,
#                         address=criminal.address,
#                         picture=criminal.picture,
#                         status='Wanted',
#                         latitude='25.3176° N',  # Replace with dynamic latitude
#                         longitude='82.9739° E'  # Replace with dynamic longitude
#                     )
#                     print(f"{criminal.name} is a wanted criminal. Details logged.")

#             cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 2)

#         cv2.imshow("Criminal Detection", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     video_capture.release()
#     cv2.destroyAllWindows()


# def detectWithWebcam(request):
#     # Load known face encodings and names dynamically from the database
#     known_face_encodings = []
#     known_face_names = []

#     criminals = Criminal.objects.all()
#     for criminal in criminals:
#         image_path = os.path.join(settings.BASE_DIR, criminal.picture)  # Ensure `picture` stores the relative path
#         if os.path.exists(image_path):
#             criminal_image = face_recognition.load_image_file(image_path)
#             criminal_encoding = face_recognition.face_encodings(criminal_image)[0]
#             known_face_encodings.append(criminal_encoding)
#             known_face_names.append(criminal)
#         else:
#             print(f"Error: Criminal image file {image_path} not found.")

#     # Initialize webcam
#     video_capture = cv2.VideoCapture(0)
#     if not video_capture.isOpened():
#         print("Error: Could not access the webcam.")
#         return

#     print("Starting real-time criminal detection. Press 'q' to quit.")

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             print("Error: Failed to read from webcam.")
#             break

#         # Convert the frame to RGB for face recognition
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Detect all face locations and encodings in the frame
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # Compare detected faces with known faces
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Civilian"
#             box_color = (0, 255, 0)  # Green for Civilian

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 criminal = known_face_names[first_match_index]
#                 name = criminal.name
#                 box_color = (0, 0, 255)  # Red for Criminal

#                 # Insert criminal spotting data into the database in real-time
#                 CriminalLastSpotted.objects.create(
#                     name=criminal.name,
#                     aadhar_no=criminal.aadhar_no,
#                     address=criminal.address,
#                     picture=criminal.picture,
#                     status=criminal.status,
#                     latitude="25.3176° N",  # Replace with dynamic GPS latitude
#                     longitude="82.9739° E",  # Replace with dynamic GPS longitude
#                 )
#                 print(f"Detected wanted criminal: {criminal.name}. Data saved to database.")

#             # Draw bounding box and label
#             cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

#         # Display the video frame with detection results
#         cv2.imshow("Real-Time Criminal Detection", frame)

#         # Exit on pressing 'q'
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release resources
#     video_capture.release()
#     cv2.destroyAllWindows()

# import cv2
# import face_recognition
# import os
# from django.conf import settings
# from django.utils.timezone import now
# from .models import Criminal, CriminalLastSpotted

# def detectWithWebcam(request):
#     # Load known face encodings and names dynamically from the database
#     known_face_encodings = []
#     known_face_names = []

#     criminals = Criminal.objects.all()
#     for criminal in criminals:
#         image_path = os.path.join(settings.BASE_DIR, criminal.picture)  # Ensure `picture` stores the relative path
#         if os.path.exists(image_path):
#             criminal_image = face_recognition.load_image_file(image_path)
#             criminal_encoding = face_recognition.face_encodings(criminal_image)[0]
#             known_face_encodings.append(criminal_encoding)
#             known_face_names.append(criminal)
#         else:
#             print(f"Error: Criminal image file {image_path} not found.")

#     # Initialize webcam
#     video_capture = cv2.VideoCapture(0)
#     if not video_capture.isOpened():
#         print("Error: Could not access the webcam.")
#         return

#     print("Starting real-time criminal detection. Press 'q' to quit.")

#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             print("Error: Failed to read from webcam.")
#             break

#         # Convert the frame to RGB for face recognition
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Detect all face locations and encodings in the frame
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             # Compare detected faces with known faces
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             name = "Detecting......"
#             # box_color = (0, 255, 0)  # Green for Civilian
#             box_color = (0, 0, 255)  # Red for Criminal

#             if True in matches:
#                 first_match_index = matches.index(True)
#                 criminal = known_face_names[first_match_index]
#                 name = criminal.name
#                 box_color = (0, 0, 255)  # Red for Criminal

#                 # Check if the criminal is already spotted
#                 created_at = CriminalLastSpotted.objects.filter(aadhar_no=criminal.aadhar_no).first()
#                 if created_at:
#                     # Update the `updated_at` timestamp
#                     created_at.updated_at = now()
#                     created_at.save()
#                     print(f"Updated spotting time for {criminal.name}.")
#                 else:
#                     # Insert new spotting data
#                     CriminalLastSpotted.objects.create(
#                         name=criminal.name,
#                         aadhar_no=criminal.aadhar_no,
#                         address=criminal.address,
#                         picture=criminal.picture,
#                         status=criminal.status,
#                         latitude="25.3176° N",  # Replace with dynamic GPS latitude
#                         longitude="82.9739° E",  # Replace with dynamic GPS longitude
#                     )
#                     print(f"New spotting record created for {criminal.name}.")

#             # Draw bounding box and label
#             cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
#             cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

#         # Display the video frame with detection results
#         cv2.imshow("Real-Time Criminal Detection", frame)

#         # Exit on pressing 'q'
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Release resources
#     video_capture.release()
#     cv2.destroyAllWindows()




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

        prsn = Criminal.objects.all()
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
            # Compare the face to the criminals present
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            name = "This is a civilian!!!"
            box_color = (0, 255, 0)  # Green for civilians
            text_color = (255, 255, 255, 255)  # White text

            # Find the distance w.r.t the faces of criminals present in the DB
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            # If a match is found, update name and box color
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                box_color = (255, 0, 0)  # Red for criminals

            # Draw a rectangle around the face
            draw.rectangle(((left, top), (right, bottom)), outline=box_color)

            # Put a label below the face
            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=box_color, outline=box_color)
            draw.text((left + 6, bottom - text_height - 5), name, fill=text_color)

        # Remove the drawing library from memory 
        del draw

        # Display the image 
        pil_image.show()
        return redirect('/success')

    return render(request, 'detect_image.html')





def detectWithWebcam(request):
    # Load known face encodings and names dynamically from the database
    known_face_encodings = []
    known_face_names = []

    criminals = Criminal.objects.all()
    for criminal in criminals:
        image_path = os.path.join(settings.BASE_DIR, criminal.picture)  # Ensure `picture` stores the relative path
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
            # Compare detected faces with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Observing Object...."
            # box_color = (0, 255, 0)  # Green for Civilian
            box_color = (0, 0, 255)  # Red for Criminal

            if True in matches:
                first_match_index = matches.index(True)
                criminal = known_face_names[first_match_index]
                name = criminal.name
                box_color = (0, 0, 255)  # Red for Criminal

                # Remove existing record if present
                CriminalLastSpotted.objects.filter(aadhar_no=criminal.aadhar_no).delete()

                # Insert updated data into the database
                CriminalLastSpotted.objects.create(
                    name=criminal.name,
                    aadhar_no=criminal.aadhar_no,
                    address=criminal.address,
                    picture=criminal.picture,
                    status=criminal.status,
                    latitude="25.3176° N",  # Replace with dynamic GPS latitude
                    longitude="82.9739° E",  # Replace with dynamic GPS longitude
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





