import cv2
import os
import shutil

# Create dataset folder
os.makedirs("dataset", exist_ok=True)

print("Choose registration mode:")
print("1. Capture from webcam")
print("2. Add existing images from folder")

mode = input("Enter 1 or 2: ").strip()

name = input("Student name: ").strip()

if name == "":
    print("Invalid student name")
    exit()

path = os.path.join("dataset", name)

os.makedirs(path, exist_ok=True)

# =========================================
# OPTION 1: Capture Images From Webcam
# =========================================
if mode == "1":

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cam.isOpened():
        print("Camera not opening")
        exit()

    count = 0

    print("\nPress S to save image")
    print("Press ESC to exit\n")

    while True:

        ret, frame = cam.read()

        if not ret:
            print("Failed to capture frame")
            break

        # Display instructions
        cv2.putText(
            frame,
            f"Images Saved: {count}/5",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("Register Face", frame)

        key = cv2.waitKey(1) & 0xFF

        # Save image
        if key == ord('s'):

            filename = os.path.join(path, f"{count}.jpg")

            cv2.imwrite(filename, frame)

            print(f"Saved: {filename}")

            count += 1

        # Auto stop after 5 images
        if count >= 5:
            print("\nRegistration complete")
            break

        # ESC key
        if key == 27:
            print("\nRegistration cancelled")
            break

    cam.release()
    cv2.destroyAllWindows()

# =========================================
# OPTION 2: Import Existing Images
# =========================================
elif mode == "2":

    source_folder = input(
        "Enter folder path containing images: "
    ).strip()

    if not os.path.exists(source_folder):
        print("Folder not found!")

    else:

        valid_extensions = (
            ".jpg",
            ".jpeg",
            ".png"
        )

        files = [
            f for f in os.listdir(source_folder)
            if f.lower().endswith(valid_extensions)
        ]

        if len(files) == 0:
            print("No image files found!")

        else:

            for i, file in enumerate(files):

                src = os.path.join(source_folder, file)

                dst = os.path.join(path, f"{i}.jpg")

                shutil.copy(src, dst)

                print(f"Added: {dst}")

            print("\nImages imported successfully")

# =========================================
# INVALID OPTION
# =========================================
else:
    print("Invalid option")