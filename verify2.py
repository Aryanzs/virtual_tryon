import cv2
import mediapipe as mp
import numpy as np

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose

def is_lower_body_suitable(image):
    with mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.5) as pose:
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)

    if not results.pose_landmarks:
        return False, "No pose landmarks detected. Please ensure you are in a well-lit area and fully visible in the frame."

    # Extract leg landmarks
    landmarks = results.pose_landmarks.landmark
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    
    # Check if legs are visible
    if not (left_knee.visibility > 0.8 and right_knee.visibility > 0.8 and
            left_ankle.visibility > 0.8 and right_ankle.visibility > 0.8):
        return False, "Legs not clearly visible. Please stand with a clear view of both knees and ankles."

    # Calculate the separation between legs
    leg_separation = abs(right_knee.x - left_knee.x) * image.shape[1]

    # Check if legs are not too wide apart
    threshold_leg_sep = image.shape[1] * 0.25
    if leg_separation > threshold_leg_sep:
        return False, "Legs are too far apart. Please stand with your legs closer together."

    # Check if legs are straight and not twisted
    if not (left_knee.y < left_ankle.y and right_knee.y < right_ankle.y and
            abs(left_ankle.x - right_ankle.x) < image.shape[1] * 0.1):
        return False, "Legs are not straight or may be twisted. Please stand with your legs straight and untwisted."

    return True, "Lower body pose is suitable for virtual try-on."

def overlay_lower_body_garment_logic(image, results, garment_image_path):
    landmarks = results.pose_landmarks.landmark
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

    # Extract hip landmarks
    left_hip_x, left_hip_y = int(left_hip.x * image.shape[1]), int(left_hip.y * image.shape[0])
    right_hip_x, right_hip_y = int(right_hip.x * image.shape[1]), int(right_hip.y * image.shape[0])

    # Calculate the center point between hips
    center_hip_x = (left_hip_x + right_hip_x) // 2
    lower_body_height = np.mean([left_hip_y, right_hip_y])

    # Define garment width and height based on body dimensions
    garment_width = int(abs(right_hip_x - left_hip_x) * 4.5 ) # Adjust width as needed
    garment_height = int((image.shape[0] - lower_body_height) * 0.95)  # Adjust height as needed

    # Calculate dynamic offsets based on garment proportions
    offset_x_percent = 1  # Adjust this percentage as needed
    offset_y_percent = 15  # Adjust this percentage as needed

    offset_x = int(garment_width * (offset_x_percent / 100))
    offset_y = int(lower_body_height * (offset_y_percent / 100))

    # Load and resize the garment image
    garment_img = cv2.imread(garment_image_path, cv2.IMREAD_UNCHANGED)
    garment_img = cv2.resize(garment_img, (int(garment_width), int(garment_height)))

    # Overlay the garment on the original image
    for y in range(garment_height):
        for x in range(garment_width):
            top_left_x = center_hip_x - garment_width // 2 + offset_x
            top_left_y = int(lower_body_height) - offset_y
            if top_left_y + y >= image.shape[0] or top_left_x + x >= image.shape[1] or garment_img[y, x][3] == 0:
                continue
            alpha = garment_img[y, x][3] / 255.0
            image[top_left_y + y, top_left_x + x] = alpha * garment_img[y, x][:3] + (1 - alpha) * image[top_left_y + y, top_left_x + x]

    return image

def overlay_lower_body_garment(model_image_path, garment_image_path, output_image_path):
    img = cv2.imread(model_image_path)
    suitable, message = is_lower_body_suitable(img)
    if suitable:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        with mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.7) as pose:
            results = pose.process(img_rgb)
            if not results.pose_landmarks:
                return None, "No pose landmarks detected."

            img_result = overlay_lower_body_garment_logic(img, results, garment_image_path)
            cv2.imwrite(output_image_path, img_result)
            return output_image_path, "Lower body try-on successful."
    else:
        return None, message

# Example usage
if __name__ == "__main__":
    model_image_path = 'path/to/model/image.jpg'
    garment_image_path = 'path/to/cloth/image.png'
    output_image_path = 'path/to/output/image.jpg'
    output_path, message = overlay_lower_body_garment(model_image_path, garment_image_path, output_image_path)
    print(message)
