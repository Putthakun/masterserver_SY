from sqlalchemy.orm import Session
from models import *
from schemas import *

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


# ดึงข้อมูล FaceVector table ทั้งหมด 
def get_all_face_vectors(db: Session):
    face_vectors = db.query(FaceVector).all()
    # ใช้ to_dict แปลงเป็น JSON-compatible format
    return [face_vector.to_dict() for face_vector in face_vectors]

def create_transaction(db: Session, transaction: TransactionRequest):
    db_transaction = Transaction(
        emp_id=transaction.emp_id,
        camera_id=transaction.camera_id,
        timestamp=transaction.timestamp
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction