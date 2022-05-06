import base64
import pyperclip


def get_base64_encoded_image():

    image_path = input("Enter image path to convert to base64: ")
    stripped_image = image_path.replace('"', "")

    with open(stripped_image, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        pyperclip.copy(base64_image)


get_base64_encoded_image()
