from fastapi import FastAPI, File, UploadFile, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO
import models
import database
from database import get_db  # นำเข้าฟังก์ชัน get_db
from redis_client import redis_client
import crud
from crud import *  # นำเข้าฟังก์ชัน get_db
from typing import List

#library for images processing
import cv2
import numpy as np
import insightface
import httpx
import json
import redis
import schemas



app = FastAPI()
router = APIRouter()

model = insightface.app.FaceAnalysis()  # โมเดล InsightFace สำหรับ Face Detection และ Embedding
model.prepare(ctx_id=1)  # ใช้ CPU (ctx_id=0) หรือ GPU (ctx_id=1)

# สร้างฐานข้อมูลตอนเริ่มต้น (ครั้งแรก)
models.Base.metadata.create_all(bind=database.engine)

# Endpoint สำหรับการอัปโหลดรูปภาพใบหน้า
@app.post("/api/upload_face/{employee_id}")
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

# แปลง vector string เป็น numpy array ขณะดึงข้อมูล
def parse_vector(vector_str):
    vector = np.fromstring(vector_str.strip('[]'), sep=' ')
    return vector

# ดึง vector จาก database มาเก็บใน redis
@app.get("/api/fetch-face-vectors-database")
def fetch_and_cache_face_vectors(db: Session = Depends(get_db)):
    # ดึงข้อมูล employee_id และ vector ทั้งหมดจากตาราง FaceVector
    face_vectors = db.query(FaceVector.emp_id, FaceVector.vector).all()
    
    # แปลงข้อมูลเป็น list ของ dict และแปลง vector เป็น numpy array
    data = []
    for fv in face_vectors:
        try:
            vector_array = np.fromstring(fv.vector.strip("[]"), sep=" ")
            data.append({"employee_id": fv.emp_id, "vector": vector_array.tolist()})
        except ValueError:
            data.append({"employee_id": fv.emp_id, "vector": None})  # จัดการกรณีแปลงไม่สำเร็จ

    try:
        # เก็บข้อมูลใน Redis
        redis_client.set("employee_vectors", json.dumps(data))
        print("Data successfully cached in Redis.")  # พิมพ์ข้อความเมื่อข้อมูลถูกเก็บใน Redis
    except redis.RedisError as e:
        print(f"Error saving to Redis: {e}")
        raise HTTPException(status_code=500, detail="Error saving data to Redis")

    return {"message": "Face vectors retrieved and cached successfully", "data": data}


# ดึงข้อมูลจาก redis ส่งไปที่ backened camera
@app.get("/api/fetch-face-vectors-redis")
async def fetch_employee_vectors():
    # ดึงข้อมูล employee_vectors จาก Redis
    employee_vectors = redis_client.get("employee_vectors")
    
    if not employee_vectors:
        raise HTTPException(status_code=404, detail="No employee vectors found in Redis")

    # แปลงข้อมูลจาก JSON เป็น Python dictionary
    vectors_data = json.loads(employee_vectors)

    return {"message": "Employee vectors retrieved successfully", "data": vectors_data}

# POST endpoint to receive the transaction
@app.post("/api/record-transaction")
async def record_transaction(transaction: schemas.TransactionRequest, db: Session = Depends(get_db)):
    try:
        db_transaction = crud.create_transaction(db=db, transaction=transaction)
        return {"status": "Transaction recorded successfully", "transaction_id": db_transaction.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording transaction: {str(e)}")