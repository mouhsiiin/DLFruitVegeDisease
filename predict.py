import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras

class FruitsVeggiesHealthClassifier:
    def __init__(self, model_path):
        """
        Initialize the classifier with a pre-trained Keras model.
        
        Args:
            model_path (str): Path to the saved Keras model file
        """
        self.model = keras.models.load_model(model_path)
        
        # Class labels for interpretable results
        self.class_labels = [
            "Apple Healthy", "Apple Rotten",
            "Banana Healthy", "Banana Rotten",
            "Bellpepper Healthy", "Bellpepper Rotten",
            "Carrot Healthy", "Carrot Rotten",
            "Cucumber Healthy", "Cucumber Rotten",
            "Grape Healthy", "Grape Rotten",
            "Guava Healthy", "Guava Rotten",
            "Jujube Healthy", "Jujube Rotten",
            "Mango Healthy", "Mango Rotten",
            "Orange Healthy", "Orange Rotten",
            "Pomegranate Healthy", "Pomegranate Rotten",
            "Potato Healthy", "Potato Rotten",
            "Strawberry Healthy", "Strawberry Rotten",
            "Tomato Healthy", "Tomato Rotten"
        ]
    
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
        
        # Convert to numpy array and normalize
        img_array = np.array(img) / 255.0
        
        # Add batch dimension
        return np.expand_dims(img_array, axis=0)
    
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
        
        # Get confidence and class
        confidence = np.max(prediction)
        class_index = int(np.argmax(prediction))
        
        return {
            'class': self.class_labels[class_index],
            'confidence': float(confidence)
        }