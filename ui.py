import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import requests
from PIL import Image, ImageTk
from io import BytesIO

class FruitsVeggiesClassifierUI:
    def __init__(self, classifier, title="Fruits & Vegetables Health Detector"):
        # Create main window with modern styling
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("900x750")
        self.root.configure(bg='#f0f0f0')

        # Store the classifier
        self.classifier = classifier

        # Create styled UI components
        self.create_widgets()

    def create_widgets(self):
        # Main container with padding and background
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Title Label
        title_label = tk.Label(main_frame, text="Fruits & Vegetables Health Detector", 
                                font=("Helvetica", 18, "bold"), 
                                bg='#f0f0f0', 
                                fg='#2c3e50')
        title_label.pack(pady=(0, 20))

        # Image display area with improved styling
        self.image_frame = tk.Frame(main_frame, bg='white', 
                                    relief=tk.RAISED, 
                                    borderwidth=2)
        self.image_frame.pack(pady=10, expand=True, fill=tk.BOTH)

        self.image_label = tk.Label(self.image_frame, 
                                    text="Select an Image", 
                                    font=("Arial", 14), 
                                    bg='white', 
                                    fg='#7f8c8d')
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # Styled Buttons Frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=10)

        # Custom button style
        button_style = {
            'font': ("Arial", 12),
            'bg': '#3498db',
            'fg': 'white',
            'activebackground': '#2980b9',
            'relief': tk.FLAT,
            'width': 25
        }

        # Local Image Button
        local_button = tk.Button(button_frame, 
                                 text="Select Local Image", 
                                 command=self.select_local_image,
                                 **button_style)
        local_button.pack(side=tk.LEFT, padx=10)

        # URL Image Button
        url_button = tk.Button(button_frame, 
                               text="Input Image URL", 
                               command=self.select_url_image,
                               **button_style)
        url_button.pack(side=tk.LEFT, padx=10)

        # Result Display Area
        self.result_frame = tk.Frame(main_frame, bg='#f0f0f0')
        self.result_frame.pack(pady=10)

        self.result_label = tk.Label(self.result_frame, 
                                     text="", 
                                     font=("Arial", 14, "bold"),
                                     bg='#f0f0f0', 
                                     fg='#2c3e50',
                                     wraplength=600)
        self.result_label.pack()

    def select_local_image(self):
        """Select and process a local image file"""
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
            img = Image.open(file_path)
            self.display_and_predict_image(img)
        except Exception as e:
            messagebox.showerror("Error", f"Could not process image: {str(e)}")

    def select_url_image(self):
        """Select and process an image from a URL"""
        url = simpledialog.askstring("Input", "Enter image URL:")
        
        if not url:
            return

        try:
            response = requests.get(url)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            self.display_and_predict_image(img)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not download image: {str(e)}")

    def display_and_predict_image(self, img):
        """Display the image and predict its health status"""
        # Resize image for display
        display_img = img.copy()
        display_img.thumbnail((600, 400))
        photo = ImageTk.PhotoImage(display_img)
        
        # Update image display
        self.image_label.config(image=photo, text="")
        self.image_label.image = photo  # Keep a reference

        try:
            # Predict health status
            prediction = self.classifier.predict(img)
            
            # Update result display with color coding
            if 'Healthy' in prediction['class']:
                result_color = '#2ecc71'  # Green for healthy
            else:
                result_color = '#e74c3c'  # Red for rotten
            
            result_text = (
                f"Prediction: {prediction['class']}\n"
                f"Confidence: {prediction['confidence']:.2%}"
            )
            
            self.result_label.config(text=result_text, fg=result_color)

        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {str(e)}")

    def run(self):
        """Start the application main loop"""
        self.root.mainloop()