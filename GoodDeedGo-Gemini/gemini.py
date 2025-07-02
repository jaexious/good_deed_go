import os
import google.generativeai as genai

# Configure API key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))

# Load Gemini model
model = genai.GenerativeModel('gemini-pro')

# Verification function
def verify_challenge_completion(photo_path):
    with open(photo_path, "rb") as img:
        image_bytes = img.read()

    response = model.generate_content([
        "Does this image show someone doing a good environmental deed?",
        genai.types.Blob(part=image_bytes, mime_type="image/jpeg")
    ])

    return response.text
