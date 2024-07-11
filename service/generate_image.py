from openai import OpenAI
from constants import app_constants


class ImageGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        # Initialise the OpenAI client with the provided API key
        self.client = OpenAI(api_key=api_key)

    def generate_image(self, prompt):
        try:
            response = self.client.images.generate(model="dall-e-3",
                                                   prompt=prompt,
                                                   n=app_constants.N,
                                                   size="1024x1024")
            image_url = response.data[0].url
            return image_url
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
