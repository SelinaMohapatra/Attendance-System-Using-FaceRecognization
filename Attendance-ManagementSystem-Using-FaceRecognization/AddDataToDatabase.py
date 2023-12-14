import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred ,{
    'databaseURL' :"https://realtimefaceattendace-df3d8-default-rtdb.firebaseio.com/"
})

ref = db.reference('Employees')

data = {
    "837480":
    {
        "name": "Selina Mohapatra",
        "major": "Computer Science",
        "starting_year": 2023,
        "total_attendance": 70,
        "standing": "G",
        "year": 1,
        "last_attendance_time": '2023-10-30 00:54:34'
    },
    "7480":
    {
        "name": "Elon Musk",
        "major": "Computer Science",
        "starting_year": 2010,
        "total_attendance": 800,
        "standing": "G",
        "year": 11,
        "last_attendance_time": '2023-10-30 00:54:34'
    },
    "1480":
    {
        "name": "Joe Biden",
        "major": "Computer Science",
        "starting_year": 2001,
        "total_attendance": 7780,
        "standing": "G",
        "year": 20,
        "last_attendance_time": '2023-10-30 00:54:34'
    },
    "639780":
    {
        "name": "Tejaswi",
        "major": "Computer Science",
        "starting_year": 2022,
        "total_attendance": 70,
        "standing": "G",
        "year": 2,
        "last_attendance_time": '2023-10-30 00:54:34'
    },
    "737180":
    {
        "name": "Sri Rakumari",
        "major": "Computer Science",
        "starting_year": 2022,
        "total_attendance": 70,
        "standing": "G",
        "year": 2,
        "last_attendance_time": '2023-10-30 00:54:34'
    }
}

for key,value in data.items():
    ref.child(key).set(value)
