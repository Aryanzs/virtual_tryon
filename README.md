# Virtual Try-On Clothes

Welcome to the Virtual Try-On Clothes project! This project allows users to upload their images and try on virtual clothes to see how they look.

## Features

- User authentication: Users can create accounts and log in to access the virtual try-on feature.
- Image upload: Users can upload their images to the platform.
- Virtual clothes try-on: Users can select clothes from the provided collection and try them on their uploaded images.
- Cloth selection: Users can choose the upper or lower body part where they want to try on the clothes.
- Result visualization: Users can view the result images showing them wearing the selected virtual clothes on their uploaded images.

## Technologies Used

- *Frontend:* HTML, CSS, JavaScript
- *Backend:* Python (Flask framework)
- *Database:* SQLite (for user authentication and storing image paths)
- *Image Processing:* OpenCV (for image manipulation and overlaying virtual clothes)
- *User Authentication:* Flask-Login (for user session management)

## Setup Instructions

1. Clone the repository:

    bash
    git clone https://github.com/your-username/virtual-try-on-clothes.git
    

2. Install dependencies:

    bash
    pip install -r requirements.txt
    

3. Set up the database:

    bash
    python setup_database.py
    

4. Run the application:

    bash
    python app.py
    

5. Access the application in your web browser Running on http://127.0.0.1:8080

## Usage

1.	Register or log in to your account.
2.	You will be redirected to the product page
3.	Chose the product you like
4.	Click on download button to download the image
5.	Now click on tryon button to try the cloth
6.	Once you click on tryon you will redirected to simple page where you have to upload your body image in straight positon and the image of product that you just downloaded and the choose what type of clothe it is upper body or lower body.
7.	After doing all this click on upload button to see the result
## Credits

- This project was created by Team Syntax Sensations.
- Virtual clothes images were sourced from google.