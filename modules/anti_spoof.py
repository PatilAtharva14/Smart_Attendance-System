import mediapipe as mp
import math

# =========================================
# INITIALIZE MEDIAPIPE
# =========================================
mp_face_mesh = mp.solutions.face_mesh

mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# =========================================
# EYE LANDMARKS
# =========================================
LEFT_EYE = [33, 160, 158, 133, 153, 144]

RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# =========================================
# BLINK SETTINGS
# =========================================
BLINK_THRESHOLD = 0.20

MIN_BLINKS = 1

# =========================================
# BLINK VARIABLES
# =========================================
blink_count = 0

blink_detected = False


# =========================================
# RESET BLINK COUNTER
# =========================================
def reset_blink():

    global blink_count
    global blink_detected

    blink_count = 0

    blink_detected = False


# =========================================
# DISTANCE FUNCTION
# =========================================
def distance(p1, p2):

    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


# =========================================
# EYE ASPECT RATIO
# =========================================
def eye_aspect_ratio(
    landmarks,
    eye_indices
):

    # Vertical distances
    v1 = distance(
        landmarks[eye_indices[1]],
        landmarks[eye_indices[5]]
    )

    v2 = distance(
        landmarks[eye_indices[2]],
        landmarks[eye_indices[4]]
    )

    # Horizontal distance
    h = distance(
        landmarks[eye_indices[0]],
        landmarks[eye_indices[3]]
    )

    # Prevent divide error
    if h == 0:
        return 0

    # =====================================
    # EAR FORMULA
    # =====================================
    ear = (v1 + v2) / (2.0 * h)

    return ear


# =========================================
# CHECK LIVENESS
# =========================================
def check_liveness(rgb_frame):

    global blink_count
    global blink_detected

    try:

        # Process frame
        results = mesh.process(
            rgb_frame
        )

        # No face detected
        if not results.multi_face_landmarks:

            return False

        # Face landmarks
        face_landmarks = (
            results.multi_face_landmarks[0]
        )

        landmarks = (
            face_landmarks.landmark
        )

        # =================================
        # LEFT EYE EAR
        # =================================
        left_ear = eye_aspect_ratio(
            landmarks,
            LEFT_EYE
        )

        # =================================
        # RIGHT EYE EAR
        # =================================
        right_ear = eye_aspect_ratio(
            landmarks,
            RIGHT_EYE
        )

        # =================================
        # AVERAGE EAR
        # =================================
        ear = (
            left_ear + right_ear
        ) / 2

        # =================================
        # BLINK DETECTION
        # =================================
        if ear < BLINK_THRESHOLD:

            if not blink_detected:

                blink_count += 1

                blink_detected = True

                print(
                    f"Blink Detected: "
                    f"{blink_count}"
                )

        else:

            blink_detected = False

        # =================================
        # LIVENESS VERIFIED
        # =================================
        if blink_count >= MIN_BLINKS:

            return True

        return False

    except Exception as e:

        print(
            f"Liveness Error: {e}"
        )

        return False