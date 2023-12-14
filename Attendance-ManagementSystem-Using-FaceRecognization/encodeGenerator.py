import cv2
import face_recognition
import pickle
# The pickle library in Python is used for serializing and deserializing Python objects.
# You don't need to install the pickle library because it is a standard library module in Python, and it is included with Python by default.
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# connect to the realtime firebase database using the json certificate key
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred ,{
    'databaseURL' :"https://realtimefaceattendace-df3d8-default-rtdb.firebaseio.com/",
    'storageBucket' :"realtimefaceattendace-df3d8.appspot.com"
})

# importing the known employee images to encode into a list
EmployeeImagePath = "EmployeeImages"
pathList = os.listdir(EmployeeImagePath)
# print(pathList)
imgList = []
employeeId = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(EmployeeImagePath, path)))
    # extract the just the id from the images name
    # print(os.path.splitext(path)[0])
    employeeId.append(os.path.splitext(path)[0])

    #upload the image to the realtime database storage
    fileName = f'{EmployeeImagePath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

# check the numvber of images in the folder
print("Uploding images to database completed.....")
print(len(imgList))
print(employeeId)


# face_recognition library loads images in the form of BGR, 
# in order to print the image you should convert it into RGB using OpenCV.
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


print("The Images are Being Encoding.....")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, employeeId]
print("Image Encoding Complete !!!")

#generate the pickle file
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("Image Encoded File Saved")


# find . -type f -name .DS_Store -delete
