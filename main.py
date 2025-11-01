from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from schemas import Todo as TodoSchema, TodoCreate
from database import SessionLocal, Base, engine
from models import Todo

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new Todo
@app.post("/todos", response_model=TodoSchema)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Read all Todos
@app.get("/todos", response_model=list[TodoSchema])
def read_all_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos

# Read single Todo by ID
@app.get("/todos/{todo_id}", response_model=TodoSchema)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# Update a Todo
@app.put("/todos/{todo_id}", response_model=TodoSchema)
def update_todo(todo_id: int, updated_todo: TodoCreate, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    for key, value in updated_todo.dict().items():
        setattr(todo, key, value)
    
    db.commit()
    db.refresh(todo)
    return todo

# Delete a Todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
