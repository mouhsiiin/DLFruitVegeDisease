import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os

class FruitsVeggiesHealthClassifier:
    def __init__(self, model_path):
        """
        Initialize the classifier with a pre-trained Keras model.
        
        Args:
            model_path (str): Path to the saved Keras model file
        """
        self.model = keras.models.load_model(model_path)
        
    def preprocess_image(self, img, target_size=(256, 256)):
        """
        Preprocess the input image for model prediction.
        
        Args:
            img (PIL.Image or numpy.ndarray): Input image
            target_size (tuple): Resize dimensions for the image
        
        Returns:
            numpy.ndarray: Preprocessed image array
        """
        # Ensure image is a PIL Image
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)
        
        # Resize and convert to RGB
        img = img.resize(target_size).convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Normalize pixel values
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    def predict(self, img):
        """
        Predict the health status of a fruit or vegetable.
        
        Args:
            img (PIL.Image or numpy.ndarray): Input image
        
        Returns:
            dict: Prediction results with probability and class
        """
        # Preprocess the image
        processed_img = self.preprocess_image(img)
        
        # Make prediction
        prediction = self.model.predict(processed_img)
        print(prediction)
        # Interpret the prediction
        confidence = np.max(prediction)
        
        return {
            'class': int(np.argmax(prediction)),
            'confidence': float(confidence)
        }

class FruitsVeggiesClassifierApp:
    def __init__(self, model_path):
        # Create main window
        self.root = tk.Tk()
        self.root.title("Fruits & Vegetables Health Classifier")
        self.root.geometry("800x700")

        # Initialize classifier
        self.classifier = FruitsVeggiesHealthClassifier(model_path)

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        # Frame for image and results
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Image display area
        self.image_label = tk.Label(main_frame, text="No image selected", 
                                    width=80, height=30,
                                    relief=tk.SUNKEN,
                                    font=("Arial", 14))
        self.image_label.pack(pady=10, expand=True, fill=tk.BOTH)

        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        # Select Image Button
        select_button = tk.Button(button_frame, text="Select Local Image", 
                                  command=self.select_local_image,
                                  font=("Arial", 12),
                                  width=20)
        select_button.pack(side=tk.LEFT, padx=10)

        # URL Image Button
        url_button = tk.Button(button_frame, text="Input Image URL", 
                               command=self.select_url_image,
                               font=("Arial", 12),
                               width=20)
        url_button.pack(side=tk.LEFT, padx=10)

        # Prediction Result Label
        self.result_label = tk.Label(main_frame, text="", 
                                     font=("Arial", 14, "bold"),
                                     wraplength=600)
        self.result_label.pack(pady=10)

    def select_local_image(self):
        # Open file dialog to select local image
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        self.process_image(file_path)

    def select_url_image(self):
        # Prompt for image URL
        url = simpledialog.askstring("Input", "Enter image URL:")
        
        if not url:
            return

        try:
            # Download image from URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Open image from bytes
            img = Image.open(BytesIO(response.content))
            
            # Display and process
            self.display_and_predict_image(img)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not download image: {str(e)}")

    def select_local_image(self):
        # Open file dialog to select local image
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            # Open local image
            img = Image.open(file_path)
            
            # Display and process
            self.display_and_predict_image(img)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not process image: {str(e)}")

    def display_and_predict_image(self, img):
        # Resize image for display
        display_img = img.copy()
        display_img.thumbnail((600, 400))
        photo = ImageTk.PhotoImage(display_img)
        
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo  # Keep a reference

        try:
            # Predict health status
            prediction = self.classifier.predict(img)
            
            # Map class to human-readable label
            class_labels = [
                    "Apple Healthy",
                    "Apple Rotten",
                    "Banana Healthy",
                    "Banana Rotten",
                    "Bellpepper Healthy",
                    "Bellpepper Rotten",
                    "Carrot Healthy",
                    "Carrot Rotten",
                    "Cucumber Healthy",
                    "Cucumber Rotten",
                    "Grape Healthy",
                    "Grape Rotten",
                    "Guava Healthy",
                    "Guava Rotten",
                    "Jujube Healthy",
                    "Jujube Rotten",
                    "Mango Healthy",
                    "Mango Rotten",
                    "Orange Healthy",
                    "Orange Rotten",
                    "Pomegranate Healthy",
                    "Pomegranate Rotten",
                    "Potato Healthy",
                    "Potato Rotten",
                    "Strawberry Healthy",
                    "Strawberry Rotten",
                    "Tomato Healthy",
                    "Tomato Rotten"
                ]
            result_text = (
                f"Prediction: {class_labels[prediction['class']]}\n"
                f"Confidence: {prediction['confidence']:.2%}"
            )
            
            self.result_label.config(text=result_text)

        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {str(e)}")

    def run(self):
        # Start the application
        self.root.mainloop()

def main():
    # Replace with the actual path to your saved Keras model
    model_path = 'best_model.keras'
    
    # Create and run the application
    app = FruitsVeggiesClassifierApp(model_path)
    app.run()

if __name__ == '__main__':
    main()