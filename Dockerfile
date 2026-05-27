FROM python:3.10-slim

# Install Node.js (needed for compiling Tailwind CSS v4)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package config and install node dependencies for Tailwind compilation
COPY package*.json ./
RUN npm install

# Copy all source files
COPY . .

# Compile Tailwind CSS stylesheet
RUN npm run build:css

# Generate the spreadsheet and train the models during container initialization
RUN python generate_dataset.py
RUN python crop_yield_prediction.py

# Hugging Face Spaces expects the app to listen on port 7860
EXPOSE 7860

# Start FastAPI via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
