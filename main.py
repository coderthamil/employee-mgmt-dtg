from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

# --- Logging setup (optional but helpful) ---
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# --- Config ---
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/My_DB"

# --- SQLAlchemy setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- ORM model ---
class EmployeeORM(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

# Create table if not exists
Base.metadata.create_all(bind=engine)

# --- Pydantic schemas ---
class Employee(BaseModel):
    name: constr(min_length=3 strip_whitespace=True)
    department: constr(min_length=3 strip_whitespace=True)
    email: EmailStr

class EmployeeOut(Employee):
    id: int

    class Config:
        orm_mode = True

# --- FastAPI app ---
app = FastAPI(title="Employee Management App")

# --- Dependency to get DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---

@app.get("/")
def intro():
    return {"message": "Welcome to Employee Management App"}

@app.post("/employee_create", response_model=EmployeeOut)
def create_employee(emp: Employee, db: Session = Depends(get_db)):
    # Check for duplicate name, email, and department
    existing = db.query(EmployeeORM).filter(
        EmployeeORM.name == emp.name,
        EmployeeORM.email == emp.email,
        EmployeeORM.department == emp.department
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Employee with this name, email, and department already exists"
        )

    db_emp = EmployeeORM(**emp.dict())
    db.add(db_emp)
    try:
        db.commit()
        db.refresh(db_emp)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate or invalid data: " + str(e.orig))
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    return db_emp

@app.get("/employees", response_model=List[EmployeeOut])
def get_all_employees(db: Session = Depends(get_db)):
    return db.query(EmployeeORM).all()

@app.get("/employees/{emp_id}", response_model=EmployeeOut)
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(EmployeeORM).filter(EmployeeORM.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.put("/employees/{emp_id}", response_model=EmployeeOut)
def update_employee(emp_id: int, emp: Employee, db: Session = Depends(get_db)):
    db_emp = db.query(EmployeeORM).filter(EmployeeORM.id == emp_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in emp.dict().items():
        setattr(db_emp, field, value)
    db.commit()
    db.refresh(db_emp)
    return db_emp

@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    db_emp = db.query(EmployeeORM).filter(EmployeeORM.id == emp_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_emp)
    db.commit()
    return {"message": f"Employee {emp_id} deleted"}