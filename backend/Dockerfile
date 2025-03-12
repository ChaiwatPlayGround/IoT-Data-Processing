# ใช้ official Python image เป็น base image
FROM python:3.9-slim

# กำหนด directory สำหรับงาน
WORKDIR /app

# คัดลอกไฟล์ที่จำเป็นจากโฟลเดอร์ปัจจุบันไปยัง container
COPY requirements.txt .

# ติดตั้ง dependencies ที่ระบุใน requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดโปรเจคทั้งหมด
COPY . .

# ตั้งค่าพอร์ตที่ Django จะรัน
EXPOSE 8000

# คำสั่งที่ใช้ในการรันโปรเจค
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
