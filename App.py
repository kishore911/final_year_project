from flask import Flask, render_template, flash, request, session
from flask import render_template, redirect, url_for, request
# from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
# from werkzeug.utils import secure_filename

import mysql.connector

import sys, fsdk, math, ctypes, time

app = Flask(__name__)
app.config['DEBUG']
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


@app.route("/")
def homepage():
    return render_template('index.html')


@app.route("/AdminLogin")
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route("/UserLogin")
def UserLogin():
    return render_template('UserLogin.html')


@app.route("/WorkerLogin")
def WorkerLogin():
    return render_template('WorkerLogin.html')


@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/Report")
def Report():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM atenttb")
    data = cur.fetchall()
    return render_template('Report.html', data=data)


@app.route("/ORemove")
def ORemove():
    id = request.args.get('id')
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
    cursor = conn.cursor()
    cursor.execute(
        "delete from ownertb where id='" + id + "'")
    conn.commit()
    conn.close()

    flash('Owner  info Remove Successfully!')

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM ownertb  ")
    data = cur.fetchall()
    return render_template('OwnerInfo.html', data=data)


@app.route("/NewWorker")
def NewWorker():
    import LiveRecognition as liv

    # del sys.modules["LiveRecognition"]
    return render_template('NewWorker.html')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb")
            data = cur.fetchall()
            return render_template('AdminHome.html', data=data)

        else:
            flash("UserName Or Password Incorrect!")
            return render_template('AdminHome.html')


@app.route("/newwork", methods=['GET', 'POST'])
def newwork():
    if request.method == 'POST':
        dname = request.form['name']

        UMobile = request.form['Mobile']
        UEmail = request.form['Email']
        Address = request.form['Address']
        Aadharno = request.form['Aadharno']
        uname = request.form['uname']
        password = request.form['password']
        conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into regtb values('','" + dname + "','" + UMobile + "','" + UEmail + "','" + Address + "','" + Aadharno + "','" +
            uname + "','" + password + "')")
        conn.commit()
        conn.close()

        flash("New User Info Saved!")
        return render_template("NewWorker.html")


@app.route("/WorkerInfo")
def WorkerInfo():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb")
    data = cur.fetchall()
    return render_template('WorkerInfo.html', data=data)


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['uname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where UserName='" + username + "' and password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            flash('Username or Password is wrong')
            return render_template('WorkerLogin.html')

        else:
            session['mob'] = data[2]
            session['email'] = data[3]

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
            cursor = conn.cursor()
            cursor.execute("truncate table temptb")
            conn.commit()
            conn.close()
            import LiveRecognition1 as liv
            liv.att()
            del sys.modules["LiveRecognition1"]
            return driver1()




def driver111():
    #import serial
    #import time
    #ser = serial.Serial('COM4', 115200, timeout=1)
    uname = session['uname']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
    cursor = conn.cursor()
    cursor.execute("SELECT * from temptb where username='" + uname + "' ")
    data = cursor.fetchone()
    if data is None:
        flash('Face  is wrong')
        return render_template('WorkerLogin.html')


    else:
        import datetime
        date = datetime.datetime.now().strftime('%d-%b-%Y')

        import cv2
        from ultralytics import YOLO

        # Load the YOLOv8 model
        model = YOLO('runs/detect/ppekit/weights/best.pt')
        # Open the video file
        # video_path = "path/to/your/video/file.mp4"
        cap = cv2.VideoCapture(0)
        dd1 = 0
        dd2 = 0
        # names: ['gloves', 'helmet', 'mask', 'no-gloves', 'no-helmet', 'no-mask', 'no-shoes', 'no-vest', 'shoes', 'vest']
        # Loop through the video frames
        while cap.isOpened():
            # Read a frame from the video
            success, frame = cap.read()

            if success:
                # Run YOLOv8 inference on the frame
                results = model(frame, conf=0.7)
                for result in results:
                    if result.boxes:
                        box = result.boxes[0]
                        class_id = int(box.cls)
                        object_name = model.names[class_id]
                        print(object_name)

                        if object_name == 'gloves' and object_name == 'helmet' and object_name == 'shoes' and object_name == 'vest':
                            dd1 += 1
                        if object_name == 'no-gloves' and object_name == 'no-helmet' and object_name == 'no-mask' and object_name == 'no-shoes':
                            dd2 += 1

                        if dd1 == 20:
                            dd1 = 0

                            #time.sleep(5)
                            #data = "A"
                            #ser.write(data.encode())  # Send the data to Arduino
                            #time.sleep(0.1)  # Add a short delay to avoid overwhelming the Arduino with data'''

                            conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                           database='3workerdb')
                            cursor = conn.cursor()
                            cursor.execute(
                                "insert into atenttb values('','" + uname + "','" + date + "','Yes')")
                            conn.commit()
                            conn.close()

                            conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                           database='3workerdb')
                            cur = conn.cursor()
                            cur.execute("SELECT * FROM atenttb where WorkerName='" + uname + "'")
                            data = cur.fetchall()
                            cap.release()
                            cv2.destroyAllWindows()

                            return render_template('WorkerHome.html', data=data)

                        if dd2 == 100:
                            #time.sleep(5)
                            #data = "B"
                            #ser.write(data.encode())  # Send the data to Arduino
                            #time.sleep(0.1)  # Add a short delay to avoid overwhelming the Arduino with data'''
                            dd2 = 0
                            conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                           database='3workerdb')
                            cursor = conn.cursor()
                            cursor.execute(
                                "insert into atenttb values('','" + uname + "','" + date + "','No')")
                            conn.commit()
                            conn.close()

                            conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                           database='3workerdb')
                            cur = conn.cursor()
                            cur.execute("SELECT * FROM atenttb where WorkerName='" + uname + "'")
                            data = cur.fetchall()

                            import winsound
                            filename = 'alert.wav'
                            winsound.PlaySound(filename, winsound.SND_FILENAME)

                            annotated_frame = results[0].plot()

                            cv2.imwrite("alert.jpg", annotated_frame)

                            cap.release()
                            cv2.destroyAllWindows()



                            return render_template('WorkerHome.html', data=data)

                # Visualize the results on the frame
                annotated_frame = results[0].plot()

                # Display the annotated frame
                cv2.imshow("YOLO11 Inference", annotated_frame)

                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        # Release the video capture object and close the display window
        #ser.close()
        cap.release()
        cv2.destroyAllWindows()



def driver1():
    #import serial
    #import time
    #ser = serial.Serial('COM4', 115200, timeout=1)
    uname = session['uname']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='3workerdb')
    cursor = conn.cursor()
    cursor.execute("SELECT * from temptb where username='" + uname + "' ")
    data = cursor.fetchone()
    if data is None:
        flash('Face  is wrong')
        return render_template('WorkerLogin.html')


    else:
        import datetime
        date = datetime.datetime.now().strftime('%d-%b-%Y')
        import cv2
        from ultralytics import YOLO

        # Load the YOLOv8 model
        model = YOLO('runs/detect/ppekit/weights/best.pt')
        cap = cv2.VideoCapture(0)

        # Counters
        dd1 = 0
        dd2 = 0

        # Required PPE items
        required_ppe = {'helmet', 'mask', 'shoes', 'vest'}
        forbidden_ppe = {'no-gloves', 'no-helmet', 'no-mask', 'no-shoes'}

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Run YOLOv8 inference
            results = model(frame, conf=0.4)

            for result in results:
                detected_items = set()

                if result.boxes:
                    for box in result.boxes:
                        class_id = int(box.cls)
                        object_name = model.names[class_id]
                        detected_items.add(object_name)
                        print(object_name)

                    # ✅ Check if ALL required PPE are present
                    if required_ppe.issubset(detected_items):
                        dd1 += 1
                    else:
                        dd1 = 0  # reset if missing something

                    # ❌ Check if any forbidden PPE are detected
                    if any(item in detected_items for item in forbidden_ppe):
                        dd2 += 1
                    else:
                        dd2 = 0  # reset if not found

                    # Actions
                    if dd1 == 20:  # reduce from 500 for faster testing
                        dd1 = 0
                        print("✅ All PPE detected: ALLOW")

                        #time.sleep(5)
                        #data = "A"
                        #ser.write(data.encode())  # Send the data to Arduino
                        #time.sleep(0.1)  # Add a short delay to avoid overwhelming the Arduino with data'''

                        conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                       database='3workerdb')
                        cursor = conn.cursor()
                        cursor.execute(
                            "insert into atenttb values('','" + uname + "','" + date + "','Yes')")
                        conn.commit()
                        conn.close()

                        conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                       database='3workerdb')
                        cur = conn.cursor()
                        cur.execute("SELECT * FROM atenttb where WorkerName='" + uname + "'")
                        data = cur.fetchall()
                        #ser.close()
                        cap.release()
                        cv2.destroyAllWindows()

                        return render_template('WorkerHome.html', data=data)

                    if dd2 == 200:
                        dd2 = 0
                        print("❌ Missing PPE: DENY")

                        #time.sleep(5)
                        #data = "B"
                        #ser.write(data.encode())  # Send the data to Arduino
                        #time.sleep(0.1)  # Add a short delay to avoid overwhelming the Arduino with data'''
                        dd2 = 0
                        conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                       database='3workerdb')
                        cursor = conn.cursor()
                        cursor.execute(
                            "insert into atenttb values('','" + uname + "','" + date + "','No')")
                        conn.commit()
                        conn.close()

                        conn = mysql.connector.connect(user='root', password='', host='localhost',
                                                       database='3workerdb')
                        cur = conn.cursor()
                        cur.execute("SELECT * FROM atenttb where WorkerName='" + uname + "'")
                        data = cur.fetchall()

                        import winsound
                        filename = 'alert.wav'
                        winsound.PlaySound(filename, winsound.SND_FILENAME)

                        annotated_frame = results[0].plot()

                        cv2.imwrite("alert.jpg", annotated_frame)

                        #ser.close()
                        cap.release()
                        cv2.destroyAllWindows()

                        return render_template('WorkerHome.html', data=data)

            # Show annotated results
            annotated_frame = results[0].plot()
            cv2.imshow("YOLO PPE Detection", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        #ser.close()
        cap.release()
        cv2.destroyAllWindows()








def sendmsg(targetno, message):
    import requests
    requests.post(
        "http://smsserver9.creativepoint.in/api.php?username=fantasy&password=596692&to=" + targetno + "&from=FSSMSS&message=Dear user  your msg is " + message + " Sent By FSMSG FSSMSS&PEID=1501563800000030506&templateid=1507162882948811640")


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
