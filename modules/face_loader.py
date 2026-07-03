import os
import face_recognition

# =========================================
# LOAD KNOWN FACES
# =========================================
def load_known_faces(dataset="dataset"):

    encodings = []

    names = []

    # =====================================
    # CHECK DATASET
    # =====================================
    if not os.path.exists(dataset):

        print(
            f"Dataset folder '{dataset}' not found"
        )

        return encodings, names

    # =====================================
    # LOOP STUDENTS
    # =====================================
    for person in os.listdir(dataset):

        folder = os.path.join(
            dataset,
            person
        )

        # SKIP NON-FOLDERS
        if not os.path.isdir(folder):

            continue

        # =================================
        # LOOP IMAGES
        # =================================
        for img_name in os.listdir(folder):

            img_path = os.path.join(
                folder,
                img_name
            )

            # =============================
            # VALID EXTENSIONS
            # =============================
            valid_extensions = (

                ".jpg",

                ".jpeg",

                ".png"

            )

            if not img_name.lower().endswith(
                valid_extensions
            ):

                continue

            try:

                # =========================
                # LOAD IMAGE
                # =========================
                img = (
                    face_recognition.load_image_file(
                        img_path
                    )
                )

                # =========================
                # ENCODE FACE
                # =========================
                face_encs = (
                    face_recognition.face_encodings(
                        img
                    )
                )

                # =========================
                # NO FACE FOUND
                # =========================
                if len(face_encs) == 0:

                    print(
                        f"No face detected in: {img_path}"
                    )

                    continue

                # =========================
                # STORE ENCODING
                # =========================
                encodings.append(
                    face_encs[0]
                )

                names.append(
                    person
                )

                print(
                    f"Loaded: {img_path}"
                )

            except Exception as e:

                print(
                    f"Error loading {img_path}: {e}"
                )

    print(
        f"Total faces loaded: {len(names)}"
    )

    return encodings, names