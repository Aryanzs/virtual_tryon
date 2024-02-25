import cv2
import mediapipe as mp
import numpy as np
#from tkinter import filedialog, Tk



# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def is_suitable_for_try_on(image):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if not results.pose_landmarks:
        return False, "No pose landmarks detected. Please ensure you are in a well-lit area and fully visible in the frame."

    # Extract shoulder landmarks
    left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    print("left hip:- ", left_hip.visibility)
    print("right hip:- ", right_hip.visibility)
    print("left shoulder:- ", left_shoulder.visibility)
    print("right shoulder:- ", right_shoulder.visibility)

    # Check if shoulders and hips are visible
    if not (left_shoulder.visibility > 0.8 and right_shoulder.visibility > 0.8):
        return False, "Shoulders not clearly visible. Please stand with a clear view of both shoulders and hips."

    # Calculate the distance between shoulders and hips
    shoulder_distance_pixels = np.sqrt(
        (left_shoulder.x - right_shoulder.x) ** 2 +
        (left_shoulder.y - right_shoulder.y) ** 2
    ) * image.shape[1]  # Assuming width is the larger dimension for distance calculation

    hip_distance_pixels = np.sqrt(
        (left_hip.x - right_hip.x) ** 2 +
        (left_hip.y - right_hip.y) ** 2
    ) * image.shape[1]  # Assuming width is the larger dimension for distance calculation

    # Check if the ratio of upper body height to total image height is below a threshold
    upper_body_height = shoulder_distance_pixels + hip_distance_pixels
    total_image_height = image.shape[0]  # Assuming height is the smaller dimension
    shoulder_hip_vector = np.array([right_shoulder.x - left_shoulder.x, right_shoulder.y - left_shoulder.y])
    hip_vector = np.array([right_hip.x - left_hip.x, right_hip.y - left_hip.y])

    # Calculate the cosine similarity to check alignment
    cosine_similarity = np.dot(shoulder_hip_vector, hip_vector) / (np.linalg.norm(shoulder_hip_vector) * np.linalg.norm(hip_vector))
    cosine_similarity = round(cosine_similarity, 3)

    print("total img ht: -", total_image_height)
    print("upperbody/total_img_ht: ", upper_body_height / total_image_height)
    print(" shoulder_hip_vector:- ", shoulder_hip_vector)
    print("hip_vector:- ", hip_vector)
    print("cosine_similarity:- ", cosine_similarity)
    cos_theta = 0.995
    # Assuming an appropriate ratio threshold is r1
    r1 = 0.6  # Adjust this value based on your requirements
    if (upper_body_height / total_image_height < r1 and total_image_height < 600) or (cosine_similarity < cos_theta):
            return False, "Not suitable.....try again with proper pose and body visibility 😭❌"
        
    return True, "Image is suitable for virtual try-on. 😁✅"

def overlay_cloth_on_model(model_image_path, cloth_image_path, output_image_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    img = cv2.imread(model_image_path)
    
    # Use clothes_image_path to read the clothes image
    img_shirt = cv2.imread(cloth_image_path, cv2.IMREAD_UNCHANGED)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        left_shoulder = (
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * img.shape[1]),
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * img.shape[0]),
        )
        right_shoulder = (
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * img.shape[1]),
            int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * img.shape[0]),
        )
        center_shoulder_x = int((left_shoulder[0] + right_shoulder[0]) / 2)
        upper_body_length = np.mean([left_shoulder[1], right_shoulder[1]])
        shirt_width = int(abs(right_shoulder[0] - left_shoulder[0]) * 1.9)
        shirt_height = int(upper_body_length * 1.2)
        offset_x_percent = 2
        offset_y_percent = 18
        offset_x = int(shirt_width * (offset_x_percent / 100))
        offset_y = int(upper_body_length * (offset_y_percent / 100))
        top_left_x = center_shoulder_x - int(shirt_width / 2)
        top_left_y = min(left_shoulder[1], right_shoulder[1]) - offset_y

        if shirt_width > 0 and shirt_height > 0:
            # Use img_shirt for the clothes image
            img_shirt = cv2.resize(img_shirt, (shirt_width, shirt_height))
            
            for y in range(shirt_height):
                for x in range(shirt_width):
                    if top_left_y + y >= img.shape[0] or top_left_x + x >= img.shape[1]:
                        continue
                    alpha = img_shirt[y, x][3] / 255.0
                    img[top_left_y + y, top_left_x + x] = (
                        img_shirt[y, x][:3] * alpha + img[top_left_y + y, top_left_x + x] * (1 - alpha)
                    )
        cv2.imwrite(output_image_path, img)
        return output_image_path, "Cloth overlay successful."

if __name__ == "__main__":
    model_image_path = 'path/to/model/image.jpg'
    cloth_image_path = 'path/to/cloth/image.png'
    output_image_path = 'path/to/output/image.jpg'
    output_path, message = overlay_cloth_on_model(model_image_path, cloth_image_path, output_image_path)
    print(message)
