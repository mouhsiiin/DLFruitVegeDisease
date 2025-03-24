from predict import FruitsVeggiesHealthClassifier
from ui import FruitsVeggiesClassifierUI

def main():
    """
    Main entry point for the Fruits & Vegetables Health Classifier application.
    
    Note: Replace 'best_model.keras' with the actual path to your trained model.
    """
    try:
        # Initialize the health classifier with the model
        model_path = 'cnn_model.keras'
        classifier = FruitsVeggiesHealthClassifier(model_path)

        # Create and run the application UI
        app = FruitsVeggiesClassifierUI(classifier)
        app.run()

    except FileNotFoundError:
        print(f"Error: Model file not found at {model_path}")
        print("Please ensure the model file path is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()