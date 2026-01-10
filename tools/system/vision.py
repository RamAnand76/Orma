
# Validates and creates a tool for Google's Vision API

import os
import google.generativeai as genai
from PIL import Image

class VisionTool:
    name = "see_image"
    description = "Analyze an image using Computer Vision. Input: Absolute file path to the image."
    
    def __init__(self):
        # Assumes GenAI is configured globally in main/core
        self.model = genai.GenerativeModel('gemini-pro-vision')
        
    def execute(self, image_path: str) -> str:
        try:
            image_path = image_path.strip().strip('"').strip("'")
            if not os.path.exists(image_path):
                return f"Error: Image not found at path: {image_path}"
                
            img = Image.open(image_path)
            
            # Identify what is in the image
            response = self.model.generate_content(["Describe this image in detail.", img])
            return response.text
            
        except Exception as e:
            return f"Vision Error: {str(e)}"
