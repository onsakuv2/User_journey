from fastapi import FastAPI, Request, Form, Depends, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
import os

# --- Database Setup ---
DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String) # Stored in plain text per simple requirements

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    category = Column(String)

Base.metadata.create_all(bind=engine)

# --- FastAPI App Setup ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Seed Initial Data ---
def seed_data():
    db = SessionLocal()
    user = db.query(User).filter(User.email == "sam@sam.com").first()
    if not user:
        new_user = User(username="sam", email="sam@sam.com", password="pass")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        sample_task = Task(
            user_id=new_user.id,
            name="Sample Task 1",
            description="This is an automatically generated task.",
            start_date=datetime.date.today(),
            end_date=datetime.date.today() + datetime.timedelta(days=7),
            category="general"
        )
        db.add(sample_task)
        db.commit()
    db.close()

seed_data()

# --- Helper Function for Auth ---
def get_current_user(request: Request, db: Session):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == int(user_id)).first()

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    # Change this:
    # return templates.TemplateResponse("landing.html", {"request": request})
    
    # To this:
    return templates.TemplateResponse(request=request, name="landing.html")

@app.post("/login")
async def login(response: Response, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email, User.password == password).first()
    if user:
        resp = RedirectResponse(url="/home", status_code=302)
        resp.set_cookie(key="user_id", value=str(user.id))
        return resp
    return RedirectResponse(url="/?error=Invalid+credentials", status_code=302)

@app.post("/register")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return RedirectResponse(url="/?error=Email+already+exists", status_code=302)
    
    new_user = User(username=username, email=email, password=password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/?msg=Registration+successful.+Please+login.", status_code=302)

@app.get("/logout")
async def logout(response: Response):
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("user_id")
    return resp

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=302)
    
    tasks = db.query(Task).filter(Task.user_id == user.id).all()
    
    # Change this:
    # return templates.TemplateResponse("home.html", {"request": request, "user": user, "tasks": tasks})
    
    # To this:
    return templates.TemplateResponse(request=request, name="home.html", context={"user": user, "tasks": tasks})

@app.get("/task", response_class=HTMLResponse)
async def task_page(request: Request, task_id: int = None, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=302)
    
    task = None
    if task_id:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()
    
    # Change this:
    # return templates.TemplateResponse("task.html", {"request": request, "user": user, "task": task})
    
    # To this:
    return templates.TemplateResponse(request=request, name="task.html", context={"user": user, "task": task})

@app.post("/task")
async def save_task(
    request: Request,
    task_id: str = Form(None), # str to handle empty strings
    name: str = Form(...),
    description: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/", status_code=302)

    sd = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    ed = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    if task_id and task_id.strip():
        # Edit existing task
        task = db.query(Task).filter(Task.id == int(task_id), Task.user_id == user.id).first()
        if task:
            task.name = name
            task.description = description
            task.start_date = sd
            task.end_date = ed
            task.category = category
            db.commit()
    else:
        # Create new task
        new_task = Task(
            user_id=user.id,
            name=name,
            description=description,
            start_date=sd,
            end_date=ed,
            category=category
        )
        db.add(new_task)
        db.commit()

    return RedirectResponse(url="/home", status_code=302)