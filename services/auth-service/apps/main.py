from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://optiroute:optiroute123@postgres:5432/optiroute")
SECRET_KEY = "tajny_klucz_123" 
ALGORITHM = "HS256"


ACCESS_TOKEN_EXPIRE_MINUTES = 3

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class UserDB(Base):
    __tablename__ = "users_simple"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class UserCreateRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

app = FastAPI(title="OptiRoute Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    time.sleep(5) 
    try:
        Base.metadata.create_all(bind=engine)
        print("Tabela users_simple gotowa.")
    except Exception as e:
        print(f"Błąd połączenia z bazą: {e}")

@app.get("/")
def read_root():
    return {"message": "Auth Service API is running."}

@app.post("/register")
def register_user(user_data: UserCreateRequest, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email jest już zajęty!")
    
    hashed_pw = get_password_hash(user_data.password)
    new_user = UserDB(email=user_data.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"message": "Użytkownik utworzony pomyślnie"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Błędny email lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}