from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), index=True)
    role = Column(String(100), index=True)

    # ความสัมพันธ์แบบ One-to-One กับ FaceVector
    face_vector = relationship("FaceVector", back_populates="employee", uselist=False)
    transactions = relationship("Transaction", back_populates="employee")

class FaceVector(Base):
    __tablename__ = "face_vectors"
    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(BigInteger, ForeignKey("employees.id"), unique=True, index=True)  # unique=True เพื่อบังคับให้ emp_id ไม่ซ้ำ
    vector = Column(Text)

    # ความสัมพันธ์กลับไปยัง Employee
    employee = relationship("Employee", back_populates="face_vector")

# แปลง numpy array เป็น JSON string
def convert_vector_to_string(vector):
    return json.dumps(vector.tolist())

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(BigInteger, ForeignKey("employees.id"), index=True)  # เปลี่ยนเป็น BigInteger
    face_vector_id = Column(Integer, ForeignKey("face_vectors.id"), index=True)  # เชื่อมกับ FaceVector
    camera_id = Column(Integer, ForeignKey("cameras.id"), index=True)  # เชื่อมกับ Camera
    timestamp = Column(DateTime, default=datetime.utcnow)  # เวลาของการเข้าร่วม
    
    # ความสัมพันธ์กับ Employee, FaceVector และ Camera
    employee = relationship("Employee", back_populates="transactions")
    camera = relationship("Camera", back_populates="transactions")

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), unique=True, index=True)  # ที่ตั้งของกล้อง
    description = Column(String(255), nullable=True)  # รายละเอียดเพิ่มเติมเกี่ยวกับกล้อง

    # ความสัมพันธ์กับ Transaction (One-to-Many)
    transactions = relationship("Transaction", back_populates="camera")
