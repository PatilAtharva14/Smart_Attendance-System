import cv2
import face_recognition
import time

from modules.face_loader import (
    load_known_faces
)

from modules.database import (
    mark_attendance
)

from modules.advanced_anti_spoof import (
    anti_spoof_check
)

# =========================================
# LOAD KNOWN FACES
# =========================================
known_encodings, known_names = (
    load_known_faces()
)

# =========================================
# POPUP MESSAGE
# =========================================
latest_message = ""

# =========================================
# FACE CONFIRMATION
# =========================================
face_confirmation = {}

# =========================================
# FRAME SKIP
# =========================================
frame_skip = 0

# =========================================
# LAST DETECTED FACE
# =========================================
last_detected_name = ""

last_detected_box = None

last_detection_time = 0

# =========================================
# GENERATE FRAMES
# =========================================
def generate_frames():

    global latest_message
    global face_confirmation
    global frame_skip

    global last_detected_name
    global last_detected_box
    global last_detection_time

    # =====================================
    # CAMERA
    # =====================================
    camera = cv2.VideoCapture(

        0,

        cv2.CAP_DSHOW

    )

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )

    if not camera.isOpened():

        print("Camera Not Opened")

        return

    while True:

        success, frame = camera.read()

        if not success:

            print("Frame Read Failed")

            break

        try:

            # =================================
            # RESIZE
            # =================================
            frame = cv2.resize(
                frame,
                (640, 480)
            )

            # =================================
            # FPS OPTIMIZATION
            # =================================
            frame_skip += 1

            process_this_frame = (
                frame_skip % 3 == 0
            )

            # =================================
            # LIGHT ENHANCEMENT
            # =================================
            frame = cv2.convertScaleAbs(

                frame,

                alpha=1.1,

                beta=10

            )

            if process_this_frame:

                # =============================
                # ANTI SPOOF
                # =============================
                confidence, status = (
                    anti_spoof_check(frame)
                )

                # =============================
                # STATUS
                # =============================
                cv2.putText(

                    frame,

                    f"{status} | {confidence:.2f}",

                    (20, 40),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.8,

                    (0, 255, 255),

                    2

                )

                # =============================
                # RGB
                # =============================
                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                # =============================
                # FACE DETECTION
                # =============================
                face_locations = (
                    face_recognition.face_locations(
                        rgb,
                        model="hog"
                    )
                )

                face_encodings = (
                    face_recognition.face_encodings(
                        rgb,
                        face_locations
                    )
                )

                # =============================
                # LOOP FACES
                # =============================
                for (
                    face_encoding,
                    face_location
                ) in zip(
                    face_encodings,
                    face_locations
                ):

                    matches = (
                        face_recognition.compare_faces(

                            known_encodings,

                            face_encoding,

                            tolerance=0.45

                        )
                    )

                    name = "Unknown"

                    # =========================
                    # MATCH FOUND
                    # =========================
                    if True in matches:

                        match_index = matches.index(
                            True
                        )

                        name = known_names[
                            match_index
                        ]

                        # =====================
                        # CACHE FACE
                        # =====================
                        last_detected_name = name

                        last_detected_box = (
                            face_location
                        )

                        last_detection_time = (
                            time.time()
                        )

                        # =====================
                        # ANTI SPOOF PASS
                        # =====================
                        if confidence >= 0.60:

                            if name not in face_confirmation:

                                face_confirmation[name] = 0

                            face_confirmation[name] += 1

                            # ================
                            # REQUIRE 8 FRAMES
                            # ================
                            if face_confirmation[name] >= 8:

                                result = mark_attendance(
                                    name
                                )

                                face_confirmation[name] = 0

                                # ================
                                # POPUPS
                                # ================
                                if result == "marked":

                                    latest_message = (

                                        f"✅ {name} Attendance Marked"

                                    )

                                elif result == "already_marked":

                                    latest_message = (

                                        f"⚠️ {name} Already Marked Today"

                                    )

                                elif result == "error":

                                    latest_message = (

                                        f"❌ Attendance Error"

                                    )

            # =================================
            # DRAW LAST FACE
            # =================================
            if last_detected_box is not None:

                elapsed = (
                    time.time()
                    - last_detection_time
                )

                # SHOW FOR 1 SECOND
                if elapsed < 1.0:

                    top, right, bottom, left = (
                        last_detected_box
                    )

                    # =========================
                    # FACE BOX
                    # =========================
                    cv2.rectangle(

                        frame,

                        (left, top),

                        (right, bottom),

                        (0, 255, 0),

                        3

                    )

                    # =========================
                    # NAME BG
                    # =========================
                    cv2.rectangle(

                        frame,

                        (left, top - 35),

                        (right, top),

                        (0, 255, 0),

                        -1

                    )

                    # =========================
                    # NAME TEXT
                    # =========================
                    cv2.putText(

                        frame,

                        last_detected_name,

                        (left + 5, top - 8),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        0.7,

                        (0, 0, 0),

                        2

                    )

            # =================================
            # ENCODE
            # =================================
            ret, buffer = cv2.imencode(
                ".jpg",
                frame
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
                f"Frame Error: {e}"
            )

            continue

    camera.release()