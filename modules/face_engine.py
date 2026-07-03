import os
import face_recognition


def load_known_faces(dataset="dataset"):

    encodings = []
    names = []

    # Check dataset folder
    if not os.path.exists(dataset):

        print(f"Dataset folder '{dataset}' not found")

        return encodings, names

    # Loop through each person folder
    for person in os.listdir(dataset):

        folder = os.path.join(dataset, person)

        # Skip non-folders
        if not os.path.isdir(folder):
            continue

        # Loop through images
        for img_name in os.listdir(folder):

            img_path = os.path.join(folder, img_name)

            # Allow only image files
            valid_extensions = (
                ".jpg",
                ".jpeg",
                ".png"
            )

            if not img_name.lower().endswith(valid_extensions):
                continue

            try:

                # Load image
                img = face_recognition.load_image_file(img_path)

                # Encode face
                face_encs = face_recognition.face_encodings(img)

                # Skip if no face found
                if len(face_encs) == 0:

                    print(
                        f"No face detected in: {img_path}"
                    )

                    continue

                # Store encoding
                encodings.append(face_encs[0])

                names.append(person)

                print(f"Loaded: {img_path}")

            except Exception as e:

                print(
                    f"Error loading {img_path}: {e}"
                )

    print(f"\nTotal faces loaded: {len(names)}")

    return encodings, names