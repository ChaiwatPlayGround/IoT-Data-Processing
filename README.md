# Project IoT Data Processing Assignment

## Overview

This project is an IoT data processing system that consists of a backend API built with Django and a frontend developed with Vue.js.

## Prerequisites

Before you begin, ensure that you have met the following requirements:

- Python 3.8+ installed
- Node.js 16+ installed
- Docker and Docker Compose (optional, for containerized setup)
- SQLite (or another database if you're using a custom one)

## 🛠 Installation & Setup

### 1️⃣ Clone Repository  
```bash
git clone https://github.com/ChaiwatPlayGround/IoT-Data-Processing.git
cd IoT-Data-Processing
```

### 2️⃣ Backend Setup (Django)

#### 📌 Install Dependencies
```bash
cd backend
python -m venv venv  # Create Virtual Environment
source venv/bin/activate  # (Linux/macOS)
venv\Scripts\activate  # (Windows)
pip install -r requirements.txt  # Install dependencies
```

#### 🔧 Configure Database
(Default is SQLite. If using PostgreSQL, modify `settings.py` accordingly)
```bash
python manage.py migrate  # Create Database
python manage.py createsuperuser  # Create admin user
```

#### 🚀 Run Backend Server
```bash
python manage.py runserver
```
API will be available at `http://127.0.0.1:8000/`

### 3️⃣ Frontend Setup (Vue.js)
```bash
cd frontend
npm install  # Install dependencies
npm run dev  # Run frontend
```
Access the application at `http://localhost:5173/`

### 📦 Docker Setup (Optional)
```bash
docker-compose up --build
```
This will automatically start both Backend and Frontend services.

### 📦 Data cleaning & anomaly detection

In this system, data cleaning and anomaly detection are performed by first handling sensor data and removing duplicates. The data is processed by calculating Z-scores for each sensor reading (temperature, humidity, and air quality) to identify outliers. Anomalies are flagged when the Z-score exceeds a threshold of 3, indicating significant deviation from the mean. The cleaned data, free from duplicates and missing values, is then analyzed, and anomalies are highlighted. This approach ensures that the data is reliable and that any unusual sensor readings are detected for further investigation.


