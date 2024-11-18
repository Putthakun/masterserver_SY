from sqlalchemy.orm import Session
from models import *


# ฟังก์ชันสำหรับสร้าง FaceVector
def create_face_vector(db: Session, emp_id: int, vector: str):
    db_face_vector = FaceVector(emp_id=emp_id, vector=vector)
    db.add(db_face_vector)
    db.commit()
    db.refresh(db_face_vector)
    return db_face_vector

# ฟังก์ชันสำหรับดึงข้อมูลพนักงานทั้งหมด
def get_employees(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Employee).offset(skip).limit(limit).all()
