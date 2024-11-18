from fastapi import FastAPI, File, UploadFile, Depends
from sqlalchemy.orm import Session
from io import BytesIO
import models
import database
from database import get_db  # นำเข้าฟังก์ชัน get_db
import crud
from crud import *  # นำเข้าฟังก์ชัน get_db

#library for images processing
import cv2
import numpy as np
import insightface


app = FastAPI()

model = insightface.app.FaceAnalysis()  # โมเดล InsightFace สำหรับ Face Detection และ Embedding
model.prepare(ctx_id=1)  # ใช้ CPU (ctx_id=0) หรือ GPU (ctx_id=1)

# สร้างฐานข้อมูลตอนเริ่มต้น (ครั้งแรก)
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI with MySQL"}

# Endpoint สำหรับการอัปโหลดรูปภาพใบหน้า
@app.post("/upload_face/{employee_id}")
async def upload_face(employee_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # อ่านข้อมูลจากไฟล์ที่อัปโหลด
    image_data = await file.read()
    image = np.array(bytearray(image_data), dtype=np.uint8)
    img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    # ตรวจจับใบหน้าด้วย InsightFace หรือ Dlib
    # (ใช้ InsightFace หรือโมเดลที่คุณใช้ในการตรวจจับใบหน้า)
    face_embeddings = detect_face_and_get_embedding(img)
    
    if face_embeddings is not None:
        # สร้างหรืออัปเดต FaceVector ในฐานข้อมูล
        # สร้าง FaceVector สำหรับพนักงาน
        face_vector = create_face_vector(db=db, emp_id=employee_id, vector=face_embeddings)
        return {"message": "Face vector uploaded successfully", "face_vector_id": face_vector.id}
    else:
        return {"message": "No face detected in the image"}

# ฟังก์ชันตรวจจับใบหน้าและแปลงเป็น Face Embedding
def detect_face_and_get_embedding(image):
    faces = model.get(image)  # ใช้ฟังก์ชัน get() สำหรับการตรวจจับใบหน้า
    if faces:
        # ได้รับ embedding ของใบหน้า
        face_embeddings = [face.embedding for face in faces]
        return face_embeddings
    return None
