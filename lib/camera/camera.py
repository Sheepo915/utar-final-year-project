import os
import time
import requests
from picamera2 import Picamera2
from multiprocessing import Pool

class CameraController:
    def __init__(self, http_url: str):
        self.http_url = http_url

        # Initialize camera
        self.camera = Picamera2()
        self.camera_config = self.camera.create_still_configuration()  # Configure for still capture
        self.camera.configure(self.camera_config)
        self.camera.start()

        # Environment variables for server config
        self.server_token = os.environ.get("SERVER_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.server_token}"} if self.server_token else {}

    def capture_image(self, file_path: str = "/tmp/image.jpg"):
        """
        Capture an image and save it to the specified file path.
        """
        print("Capturing image...")
        self.camera.capture_file(file_path)
        print(f"Image saved at {file_path}")
        return file_path

    def send_image(self, image_path: str):
        """
        Sends the captured image to the HTTP server.
        """
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            print(f"Sending image {image_path} to {self.http_url}")
            response = requests.post(self.http_url, headers=self.headers, files=files)
            print(f"Server response: {response.status_code} - {response.text}")

    def process_image(self):
        """
        Capture and send an image in one go.
        """
        image_path = self.capture_image()
        self.send_image(image_path)

    def run_continuously(self, interval: int = 10):
        """
        Continuously capture and send images at a specified interval.
        """
        while True:
            self.process_image()
            time.sleep(interval)
            

class CameraControllerTest:
    def __init__(self, save_directory: str = "/tmp/test_images"):
        # Initialize the save directory and camera
        self.save_directory = save_directory
        os.makedirs(self.save_directory, exist_ok=True)
        
        self.camera = Picamera2()
        self.camera_config = self.camera.create_still_configuration()
        self.camera.configure(self.camera_config)
        self.camera.start()

    def capture_image(self, file_name: str):
        """
        Capture an image and save it with the specified file name.
        """
        file_path = os.path.join(self.save_directory, file_name)
        print(f"Capturing image to {file_path}")
        self.camera.capture_file(file_path)
        print(f"Image saved at {file_path}")
        return file_path

    def run_continuously(self, interval: int = 5, image_count: int = 10):
        """
        Continuously capture images at the specified interval and save them locally.
        Captures a total of 'image_count' images.
        """
        for i in range(image_count):
            file_name = f"test_image_{i+1}.jpg"
            self.capture_image(file_name)
            time.sleep(interval)
            

# Example usage
if __name__ == "__main__":
    server_url = "http://your-server.com/upload"  # Placeholder server URL, replace with actual
    
    controller = CameraControllerTest(save_directory="/tmp/test_images")
    
    # Capture 10 images, with a 5-second interval between each
    controller.run_continuously(interval=5, image_count=10)

    # controller = CameraController(http_url=server_url)

    # # Capture and send image every 10 seconds
    # controller.run_continuously(interval=10)
