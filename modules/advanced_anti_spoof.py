import cv2
import mediapipe as mp
import numpy as np
from skimage.feature import local_binary_pattern

# =========================================
# MEDIAPIPE
# =========================================
mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(

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
# GLOBALS
# =========================================
blink_detected = False

blink_count = 0

stable_frames = 0

head_movement_detected = False

last_nose_x = None

last_nose_y = None

# =========================================
# DISTANCE
# =========================================
def distance(p1, p2):

    return np.sqrt(

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

    v1 = distance(

        landmarks[eye_indices[1]],

        landmarks[eye_indices[5]]

    )

    v2 = distance(

        landmarks[eye_indices[2]],

        landmarks[eye_indices[4]]

    )

    h = distance(

        landmarks[eye_indices[0]],

        landmarks[eye_indices[3]]

    )

    ear = (v1 + v2) / (2.0 * h)

    return ear

# =========================================
# TEXTURE ANALYSIS
# =========================================
def texture_score(face_crop):

    try:

        gray = cv2.cvtColor(

            face_crop,

            cv2.COLOR_BGR2GRAY

        )

        lbp = local_binary_pattern(

            gray,

            P=8,

            R=1,

            method="uniform"

        )

        variance = np.var(lbp)

        # =================================
        # NORMALIZED SCORE
        # =================================
        score = min(

            variance / 80,

            1.0

        )

        return score

    except:

        return 0.0

# =========================================
# HEAD MOVEMENT
# =========================================
def detect_head_movement(

    nose_x,

    nose_y

):

    global last_nose_x
    global last_nose_y
    global head_movement_detected

    if last_nose_x is None:

        last_nose_x = nose_x
        last_nose_y = nose_y

        return False

    dx = abs(nose_x - last_nose_x)

    dy = abs(nose_y - last_nose_y)

    last_nose_x = nose_x
    last_nose_y = nose_y

    # =====================================
    # NATURAL MOVEMENT
    # =====================================
    if dx > 0.005 or dy > 0.005:

        head_movement_detected = True

    return head_movement_detected

# =========================================
# RESET
# =========================================
def reset_liveness():

    global blink_detected
    global blink_count
    global stable_frames
    global head_movement_detected
    global last_nose_x
    global last_nose_y

    blink_detected = False

    blink_count = 0

    stable_frames = 0

    head_movement_detected = False

    last_nose_x = None

    last_nose_y = None

# =========================================
# MAIN ANTI SPOOF
# =========================================
def anti_spoof_check(frame):

    global blink_count
    global blink_detected
    global stable_frames

    rgb = cv2.cvtColor(

        frame,

        cv2.COLOR_BGR2RGB

    )

    results = face_mesh.process(rgb)

    # =====================================
    # NO FACE
    # =====================================
    if not results.multi_face_landmarks:

        reset_liveness()

        return 0.0, "No Face"

    face_landmarks = (

        results.multi_face_landmarks[0]

    )

    landmarks = face_landmarks.landmark

    confidence = 0.0

    # =====================================
    # FACE PRESENT
    # =====================================
    confidence += 0.35

    stable_frames += 1

    # =====================================
    # BLINK DETECTION
    # =====================================
    left_ear = eye_aspect_ratio(

        landmarks,

        LEFT_EYE

    )

    right_ear = eye_aspect_ratio(

        landmarks,

        RIGHT_EYE

    )

    ear = (left_ear + right_ear) / 2

    # =====================================
    # BETTER BLINK THRESHOLD
    # =====================================
    if ear < 0.23:

        if not blink_detected:

            blink_count += 1

            blink_detected = True

    else:

        blink_detected = False

    if blink_count >= 1:

        confidence += 0.25

    # =====================================
    # HEAD MOVEMENT
    # =====================================
    nose = landmarks[1]

    moved = detect_head_movement(

        nose.x,

        nose.y

    )

    if moved:

        confidence += 0.20

    # =====================================
    # FACE CROP
    # =====================================
    h, w, _ = frame.shape

    x1 = int(landmarks[234].x * w)

    y1 = int(landmarks[10].y * h)

    x2 = int(landmarks[454].x * w)

    y2 = int(landmarks[152].y * h)

    # SAFE CROP
    x1 = max(0, x1)
    y1 = max(0, y1)

    x2 = min(w, x2)
    y2 = min(h, y2)

    face_crop = frame[y1:y2, x1:x2]

    # =====================================
    # TEXTURE SCORE
    # =====================================
    if face_crop.size != 0:

        texture = texture_score(

            face_crop

        )

        confidence += texture * 0.15

    # =====================================
    # STABLE FRAMES
    # =====================================
    if stable_frames >= 8:

        confidence += 0.10

    # =====================================
    # LIMIT
    # =====================================
    confidence = min(confidence, 1.0)

    # =====================================
    # FINAL RESULT
    # =====================================
    if confidence >= 0.60:

        return confidence, "Real Face Verified"

    elif confidence >= 0.40:

        return confidence, "Verifying..."

    else:

        return confidence, "Spoof Suspected"