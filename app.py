from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    Response,
    session
)

import os
import cv2
import time
import pandas as pd
import plotly.express as px
import face_recognition

from modules.database import (

    init_db,

    register_user,

    login_user,

    get_student_attendance

)

from modules.analytics import (

    get_data,

    get_total_attendance,

    get_total_students,

    get_today_attendance,

    get_attendance_percentage,

    get_top_attendees,

    get_daily_trend,

    get_weekday_stats,

    generate_ai_insights

)

from modules.attendance_manager import (

    generate_frames,

    latest_message

)

# =========================================
# INITIALIZE FLASK
# =========================================
app = Flask(__name__)

app.secret_key = "attendance_secret_key"

# =========================================
# INITIALIZE DATABASE
# =========================================
init_db()

# =========================================
# HOME
# =========================================
@app.route("/")
def home():

    return redirect("/login")

# =========================================
# LOGIN
# =========================================
@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        role = request.form.get(
            "role"
        )

        user = login_user(

            username,

            password,

            role

        )

        if user:

            session["username"] = username

            session["role"] = role

            if role == "admin":

                return redirect(
                    "/admin"
                )

            elif role == "faculty":

                return redirect(
                    "/faculty"
                )

            elif role == "student":

                return redirect(
                    "/student"
                )

        flash(
            "❌ Invalid Credentials"
        )

    return render_template(
        "login.html"
    )

# =========================================
# USER REGISTER
# =========================================
@app.route(
    "/user_register",
    methods=["GET", "POST"]
)
def user_register():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        role = request.form.get(
            "role"
        )

        success = register_user(

            username,

            password,

            role

        )

        if success:

            flash(
                "✅ Registration Successful"
            )

            return redirect(
                "/login"
            )

        else:

            flash(
                "⚠️ User Already Exists"
            )

    return render_template(
        "user_register.html"
    )

# =========================================
# ADMIN DASHBOARD
# =========================================
@app.route("/admin")
def admin():

    if session.get("role") != "admin":

        return redirect("/login")

    return render_template(
        "admin_dashboard.html"
    )

# =========================================
# FACULTY DASHBOARD
# =========================================
@app.route("/faculty")
def faculty():

    if session.get("role") != "faculty":

        return redirect("/login")

    return render_template(
        "faculty_dashboard.html"
    )

# =========================================
# FACULTY FACE REGISTER PAGE
# =========================================
@app.route(
    "/faculty_register_face",
    methods=["GET"]
)
def faculty_register_face():

    if session.get("role") != "faculty":

        return redirect("/login")

    username = session.get(
        "username"
    )

    return render_template(

        "faculty_face_register.html",

        username=username

    )

# =========================================
# OPTIMIZED FACULTY CAMERA FEED
# =========================================
@app.route("/faculty_register_feed")
def faculty_register_feed():

    def generate_faculty_frames():

        cam = cv2.VideoCapture(

            0,

            cv2.CAP_DSHOW

        )

        # =================================
        # LOW RESOLUTION FOR SPEED
        # =================================
        cam.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            320
        )

        cam.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            240
        )

        if not cam.isOpened():

            print(
                "Faculty Camera Error"
            )

            return

        frame_skip = 0

        while True:

            success, frame = cam.read()

            if not success:
                break

            try:

                # =========================
                # SMALL FRAME
                # =========================
                frame = cv2.resize(
                    frame,
                    (320, 240)
                )

                frame_skip += 1

                # =========================
                # PROCESS EVERY 3RD FRAME
                # =========================
                if frame_skip % 3 == 0:

                    rgb = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB
                    )

                    faces = (
                        face_recognition.face_locations(
                            rgb,
                            model="hog"
                        )
                    )

                    for (
                        top,
                        right,
                        bottom,
                        left
                    ) in faces:

                        # =================
                        # FACE BOX
                        # =================
                        cv2.rectangle(

                            frame,

                            (left, top),

                            (right, bottom),

                            (0, 255, 0),

                            2

                        )

                        # =================
                        # TEXT
                        # =================
                        cv2.putText(

                            frame,

                            "Face Detected",

                            (left, top - 10),

                            cv2.FONT_HERSHEY_SIMPLEX,

                            0.5,

                            (0, 255, 255),

                            2

                        )

                # =========================
                # LOW JPEG QUALITY
                # =========================
                ret, buffer = cv2.imencode(

                    ".jpg",

                    frame,

                    [
                        int(
                            cv2.IMWRITE_JPEG_QUALITY
                        ),
                        60
                    ]

                )

                frame = buffer.tobytes()

                yield (

                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n'
                    + frame +
                    b'\r\n'

                )

            except Exception as e:

                print(
                    f"Faculty Feed Error: {e}"
                )

                continue

        cam.release()

    return Response(

        generate_faculty_frames(),

        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        )

    )

# =========================================
# SAVE FACULTY FACE
# =========================================
@app.route(
    "/save_faculty_face",
    methods=["POST"]
)
def save_faculty_face():

    if session.get("role") != "faculty":

        return redirect("/login")

    username = session.get(
        "username"
    )

    path = os.path.join(
        "dataset",
        username
    )

    os.makedirs(
        path,
        exist_ok=True
    )

    cam = cv2.VideoCapture(0)

    count = 0

    while count < 20:

        success, frame = cam.read()

        if not success:
            break

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        faces = (
            face_recognition.face_locations(
                rgb,
                model="hog"
            )
        )

        if len(faces) > 0:

            filename = os.path.join(
                path,
                f"{count}.jpg"
            )

            cv2.imwrite(
                filename,
                frame
            )

            count += 1

            time.sleep(0.2)

    cam.release()

    flash(

        f"✅ {username} Faculty Face Registered Successfully"

    )

    return redirect(
        "/faculty"
    )

# =========================================
# FACULTY ATTENDANCE PAGE
# =========================================
@app.route(
    "/faculty_attendance"
)
def faculty_attendance():

    if session.get("role") != "faculty":

        return redirect("/login")

    return render_template(
        "faculty_attendance.html"
    )

# =========================================
# STUDENT DASHBOARD
# =========================================
@app.route("/student")
def student():

    if session.get("role") != "student":

        return redirect("/login")

    username = session.get(
        "username"
    )

    attendance_data = (
        get_student_attendance(
            username
        )
    )

    total = len(
        attendance_data
    )

    return render_template(

        "student_dashboard.html",

        username=username,

        attendance_data=attendance_data,

        total=total

    )

# =========================================
# STUDENT FACE REGISTER PAGE
# =========================================
@app.route(
    "/student_register_face",
    methods=["GET"]
)
def student_register_face():

    if session.get("role") != "student":

        return redirect("/login")

    username = session.get(
        "username"
    )

    return render_template(

        "student_face_register.html",

        username=username

    )

# =========================================
# SAVE STUDENT FACE
# =========================================
@app.route(
    "/save_student_face",
    methods=["POST"]
)
def save_student_face():

    if session.get("role") != "student":

        return redirect("/login")

    username = session.get(
        "username"
    )

    path = os.path.join(
        "dataset",
        username
    )

    os.makedirs(
        path,
        exist_ok=True
    )

    cam = cv2.VideoCapture(0)

    count = 0

    while count < 20:

        success, frame = cam.read()

        if not success:
            break

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        faces = (
            face_recognition.face_locations(
                rgb,
                model="hog"
            )
        )

        if len(faces) > 0:

            filename = os.path.join(
                path,
                f"{count}.jpg"
            )

            cv2.imwrite(
                filename,
                frame
            )

            count += 1

            time.sleep(0.2)

    cam.release()

    flash(

        f"✅ {username} Face Registered Successfully"

    )

    return redirect(
        "/student"
    )

# =========================================
# STUDENT ATTENDANCE PAGE
# =========================================
@app.route(
    "/student_attendance"
)
def student_attendance():

    if session.get("role") != "student":

        return redirect("/login")

    return render_template(
        "student_attendance.html"
    )

# =========================================
# ATTENDANCE PAGE
# =========================================
@app.route("/attendance")
def attendance():

    return render_template(
        "attendance.html"
    )

# =========================================
# LIVE VIDEO FEED
# =========================================
@app.route("/video_feed")
def video_feed():

    try:

        return Response(

            generate_frames(),

            mimetype=(
                "multipart/x-mixed-replace; "
                "boundary=frame"
            )

        )

    except Exception as e:

        print(
            f"Video Feed Error: {e}"
        )

        return "Camera Error"

# =========================================
# DASHBOARD
# =========================================
@app.route("/dashboard")
def dashboard():

    try:

        df = get_data()

        if df.empty:

            return render_template(
                "dashboard.html",
                no_data=True
            )

        total_attendance = (
            get_total_attendance(df)
        )

        total_students = (
            get_total_students(df)
        )

        today_attendance = (
            get_today_attendance(df)
        )

        attendance_percent = (
            get_attendance_percentage(df)
        )

        top_attendees = (
            get_top_attendees(df)
        )

        insights = (
            generate_ai_insights(df)
        )

        fig1 = px.bar(
            top_attendees,
            x="Student",
            y="Attendance Count",
            title="Top Attendance",
            text_auto=True
        )

        fig1.update_layout(
            template="plotly_dark"
        )

        graph1 = fig1.to_html(
            full_html=False
        )

        records = df.to_dict(
            orient="records"
        )

        return render_template(

            "dashboard.html",

            records=records,

            total_attendance=total_attendance,

            total_students=total_students,

            today_attendance=today_attendance,

            attendance_percent=attendance_percent,

            top_attendees=top_attendees.to_dict(
                orient="records"
            ),

            graph1=graph1,

            insights=insights

        )

    except Exception as e:

        return (
            f"Dashboard Error: {e}"
        )

# =========================================
# LIVE MESSAGE
# =========================================
@app.route("/get_message")
def get_message():

    return {
        "message": latest_message
    }

# =========================================
# LOGOUT
# =========================================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    app.run(
        debug=True,
        threaded=True
    )