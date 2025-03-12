# ใช้ official Node.js image เป็น base image
FROM node:16

# กำหนด directory สำหรับงาน
WORKDIR /app

# คัดลอกไฟล์ package.json และ package-lock.json ก่อนเพื่อใช้ในการติดตั้ง dependencies
COPY package*.json ./

# ติดตั้ง dependencies
RUN npm install

# คัดลอกโค้ดโปรเจคทั้งหมด
COPY . .

# สร้างโปรเจค Vue.js
RUN npm run build

# ตั้งค่าพอร์ตที่ Vue.js จะรัน
EXPOSE 8080

# คำสั่งที่ใช้ในการรัน frontend (หลังจาก build แล้ว)
CMD ["npm", "run", "serve"]
