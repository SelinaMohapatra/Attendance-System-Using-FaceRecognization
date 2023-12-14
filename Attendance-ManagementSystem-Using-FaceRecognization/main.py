import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime


# connect to the realtime firebase database using the json certificate key
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://realtimefaceattendace-df3d8-default-rtdb.firebaseio.com/",
    'storageBucket': "realtimefaceattendace-df3d8.appspot.com"
})

bucket = storage.bucket()

# turnon the webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# load the image for the background
imgBackground = cv2.imread('static/images/background.png')

# Importing the mode images into a list and append it to the background image
folderModePath = 'static/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Loading the encoding pickle file
print("Loading the Image Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, employeeId = encodeListKnownWithIds
# print(employeeId)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    # Resize the image in the current frame so thats it doesnt take much space
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # providing the location of the current face so that we can generate the encodings to compare with known encoding
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # overlay the webcam on the background
    imgBackground[162:162 + 480, 55:55 + 640] = img
    # add the mode images to the background
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    # Set a confidence threshold
    confidence_threshold = 0.7

    if faceCurFrame:
        # zip is used if we want to use for loop for both the parameters instead for writing 2 loops
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            # Check the confidence of face detection
            if face_recognition.compare_faces(encodeListKnown, encodeFace)[0] < confidence_threshold:
                continue  # Skip faces with low confidence
            
            # comparing the current encodings with known encoding to find a match
            matches = face_recognition.compare_faces(
                encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(
                encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            # To get the index of least value of the faceDis
            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(employeeId[matchIndex])
                y1, x2, y2, x1 = faceLoc
                # we reduced it earlier hence for original size
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                # creates a box when face detected
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = employeeId[matchIndex]
                # once face is detected change the counter to 1
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    # cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Get the Data
                employeeInfo = db.reference(f'Employees/{id}').get()
                # print(employeeInfo)
                # Get the Image from the storage
                blob = bucket.get_blob(f'EmployeeImages/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgEmployee = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update data of attendance
                datetimeObject = datetime.strptime(employeeInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (
                    datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'Employees/{id}')
                    employeeInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(
                        employeeInfo['total_attendance'])
                    ref.child('last_attendance_time').set(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 +
                                  414] = imgModeList[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 +
                              414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(employeeInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(employeeInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(employeeInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(employeeInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(employeeInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(
                        employeeInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(employeeInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgEmployee

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    employeeInfo = []
                    imgEmployee = []
                    imgBackground[44:44 + 633, 808:808 +
                                  414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    # This displayes the webcam with background
    cv2.imshow("Face Attendance", imgBackground)
    # cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
