FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure we have the model file
RUN echo "Make sure cnn_model.keras exists in your directory before building"

# Expose the port the app runs on
EXPOSE 5050

# Command to run the application
CMD ["python", "app.py"]