from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import base64
from PIL import Image
from rembg import remove

# Import your custom functions
from verify import overlay_cloth_on_model
from verify2 import overlay_lower_body_garment

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/homw')
def homw():
    return render_template('homw.html')

@app.route('/login')
def login():
    return render_template('login.html')


# Directory setup
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = os.path.join('static', 'results')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

# this function is to remove background

def remove_background(input_path, output_path):
    try:
        # Read the image as bytes
        with open(input_path, 'rb') as input_file:
            input_bytes = input_file.read()

        # Remove the background
        output_bytes = remove(input_bytes)

        # Save the output bytes to an image file
        with open(output_path, 'wb') as output_file:
            output_file.write(output_bytes)
            
        print("Background removal successful.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        model_image = request.files.get('model_image')
        clothes_image = request.files.get('clothes_image')
        garment_type = request.form.get('garment_type')

        if model_image and clothes_image:
            model_filename = secure_filename(model_image.filename)
            clothes_filename = secure_filename(clothes_image.filename)

            model_image_path = os.path.join(app.config['UPLOAD_FOLDER'], model_filename)
            clothes_image_path = os.path.join(app.config['UPLOAD_FOLDER'], clothes_filename)
            clothes_no_bg_path = os.path.join(app.config['UPLOAD_FOLDER'], 'no_bg_' + clothes_filename)  # Path for the cloth image after background removal
            output_filename = 'output_' + model_filename
            output_image_path = os.path.join(app.config['STATIC_FOLDER'], output_filename)

            model_image.save(model_image_path)
            clothes_image.save(clothes_image_path)

            # Remove background from clothes image
            if not remove_background(clothes_image_path, clothes_no_bg_path):
                return jsonify({'error': 'Failed to remove background from clothes image'})

            # Decide which function to use based on the garment type
            if garment_type == 'lower_body':
                output_path, message = overlay_lower_body_garment(model_image_path, clothes_no_bg_path, output_image_path)
            elif garment_type == 'upper_body':
                output_path, message = overlay_cloth_on_model(model_image_path, clothes_no_bg_path, output_image_path)
            else:
                return jsonify({'error': 'Invalid garment type specified'})

            if output_path:
                # Encode the output image to base64 for displaying directly in the HTML
                with open(output_image_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                return render_template('result.html', img_data=img_data)
            else:
                return jsonify({'error': message})
        else:
            return jsonify({'error': 'Files not provided or invalid file names'})

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True,port=8080)
