import os
import time
import uuid
import csv
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://optiroute:optiroute123@postgres:5432/optiroute",
)
SECRET_KEY = "tajny_klucz_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=False)
    surname = Column(String, index=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class JobDB(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String, default="PENDING", index=True)
    input_file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    result = Column(JSON, nullable=True)


class RequestDB(Base):
    __tablename__ = "requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, default="to do", server_default="to do", index=True)
    courier_number = Column(String, nullable=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserCreateRequest(BaseModel):
    name: str
    surname: str
    email: str
    password: str


class AdminUserCreateRequest(BaseModel):
    name: str
    surname: str
    email: str
    password: str
    role: str = "user"


class Token(BaseModel):
    name: str
    surname: str
    role: str
    access_token: str
    token_type: str


class JobCreate(BaseModel):
    input_file_path: Optional[str] = None
    status: str = "PENDING"


class JobResponse(BaseModel):
    id: uuid.UUID
    status: str
    input_file_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class RequestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None


class RequestAssign(BaseModel):
    courier_number: str


class RequestResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    location: Optional[str]
    status: str
    courier_number: Optional[str]
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


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


def write_locations_csv(rows, filename: str):
    export_dir = "/app/exports"
    os.makedirs(export_dir, exist_ok=True)
    file_path = os.path.join(export_dir, filename)

    # utf-8-sig to zachować polskie znaki przy otwieraniu w Excelu
    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        for r in rows:
            writer.writerow([r.location or ""])

    return file_path


def write_requests_csv(db: Session):
    rows = db.query(RequestDB).order_by(RequestDB.created_at.desc()).all()
    return write_locations_csv(rows, "requests.csv")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidłowe dane uwierzytelniające",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@app.on_event("startup")
def startup():
    time.sleep(5)
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Auth Service API is running."}


@app.get("/me")
def read_me(current_user: UserDB = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "surname": current_user.surname,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at,
    }


@app.post("/me/password")
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    if not verify_password(payload.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Stare hasło jest niepoprawne")

    current_user.password = get_password_hash(payload.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"message": "Hasło zostało zmienione"}


@app.post("/register", status_code=201)
def register_user(user_data: UserCreateRequest, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email jest już zajęty")

    hashed_pw = get_password_hash(user_data.password)
    new_user = UserDB(
        name=user_data.name,
        surname=user_data.surname,
        email=user_data.email,
        password=hashed_pw,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Użytkownik utworzony pomyślnie", "email": new_user.email}


@app.get("/admin/users")
def list_users(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Dostęp tylko dla administratorów")
    
    users = db.query(UserDB).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
        }
        for user in users
    ]


@app.post("/admin/users", status_code=201)
def create_user_by_admin(
    user_data: AdminUserCreateRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Dostęp tylko dla administratorów")
    
    # Sprawdź czy email jest wolny
    existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email jest już zajęty")
    
    # Walidacja roli
    valid_roles = ["admin", "driver", "user"]
    if user_data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Nieprawidłowa rola. Dozwolone: {', '.join(valid_roles)}")
    
    # Tworzenie użytkownika
    hashed_pw = get_password_hash(user_data.password)
    new_user = UserDB(
        name=user_data.name,
        surname=user_data.surname,
        email=user_data.email,
        password=hashed_pw,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "Użytkownik utworzony pomyślnie",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "role": new_user.role
        }
    }


@app.get("/admin/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobDB).order_by(JobDB.created_at.desc()).all()
    return [
        {
            "id": job.id,
            "status": job.status,
            "input_file_path": job.input_file_path,
            "created_at": job.created_at,
        }
        for job in jobs
    ]


@app.post("/admin/jobs", status_code=201)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    new_job = JobDB(
        status=job_data.status or "PENDING",
        input_file_path=job_data.input_file_path,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return {
        "id": new_job.id,
        "status": new_job.status,
        "input_file_path": new_job.input_file_path,
        "created_at": new_job.created_at,
    }


@app.post("/requests", response_model=RequestResponse, status_code=201)
def create_request(
    req: RequestCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    new_req = RequestDB(
        title=req.title,
        description=req.description,
        location=req.location,
        status="to do",
        courier_number=None,
        user_id=current_user.id,
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    write_requests_csv(db)
    return new_req


@app.get("/requests/mine", response_model=list[RequestResponse])
def list_my_requests(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    return (
        db.query(RequestDB)
        .filter(RequestDB.user_id == current_user.id)
        .order_by(RequestDB.created_at.desc())
        .all()
    )


@app.get("/requests/assigned", response_model=list[RequestResponse])
def list_assigned_requests(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # Przyjmujemy, że numer kuriera to email kierowcy
    courier_identifier = current_user.email
    return (
        db.query(RequestDB)
        .filter(RequestDB.courier_number == courier_identifier)
        .order_by(RequestDB.created_at.desc())
        .all()
    )


@app.get("/admin/requests", response_model=list[RequestResponse])
def list_requests(db: Session = Depends(get_db)):
    return db.query(RequestDB).order_by(RequestDB.created_at.desc()).all()


@app.get("/admin/requests/export")
def export_requests_csv(db: Session = Depends(get_db)):
    rows = db.query(RequestDB).order_by(RequestDB.created_at.desc()).all()
    file_path = write_locations_csv(rows, "requests.csv")
    return FileResponse(file_path, media_type="text/csv", filename="requests.csv")


@app.delete("/admin/requests/{request_id}", status_code=204)
def delete_request(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Usuń zlecenie (tylko admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    request = db.query(RequestDB).filter(RequestDB.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    db.delete(request)
    db.commit()
    return None


@app.patch("/admin/requests/{request_id}/assign", response_model=RequestResponse)
def assign_request(
    request_id: uuid.UUID,
    assign_data: RequestAssign,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    """Przypisz zlecenie do kierowcy (tylko admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    request = db.query(RequestDB).filter(RequestDB.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Sprawdź czy kierowca istnieje
    driver = db.query(UserDB).filter(
        UserDB.email == assign_data.courier_number,
        UserDB.role == "driver"
    ).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    request.courier_number = assign_data.courier_number
    request.status = "assigned"
    db.commit()
    db.refresh(request)
    return request


@app.get("/requests/assigned/export")
def export_assigned_requests_csv(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    courier_identifier = current_user.email
    rows = (
        db.query(RequestDB)
        .filter(RequestDB.courier_number == courier_identifier)
        .order_by(RequestDB.created_at.desc())
        .all()
    )
    file_path = write_locations_csv(rows, f"requests_{current_user.id}_assigned.csv")
    return FileResponse(file_path, media_type="text/csv", filename="requests_assigned.csv")


@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Błędny email lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "sub": user.email,
        "name": user.name,
        "surname": user.surname,
        "role": user.role,
    }
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": user.email,
        "name": user.name,
        "surname": user.surname,
        "role": user.role,
    }


@app.get("/geocode/search")
async def geocode_search(q: str, limit: int = 20):
    """
    Proxy endpoint dla Nominatim API (OpenStreetMap)
    Format: <miasto>, <ulica> <numer>
    """
    if not q or len(q) < 3:
        return []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": q,
                    "format": "json",
                    "limit": limit,
                    "addressdetails": 1,
                    "countrycodes": "pl"
                },
                headers={
                    "User-Agent": "OptiRoute-App/1.0"
                },
                timeout=10.0
            )
            response.raise_for_status()
            results = response.json()
            
            # Formatuj wyniki do struktury: <miasto>, <ulica> <numer>
            formatted_results = []
            seen = set()  # Unikanie duplikatów
            
            for result in results:
                address = result.get("address", {})
                
                # Pobierz komponenty adresu
                city = (
                    address.get("city") or 
                    address.get("town") or 
                    address.get("village") or 
                    address.get("municipality") or
                    address.get("county")
                )
                
                street = address.get("road")
                house_number = address.get("house_number", "")
                
                # Jeśli mamy przynajmniej miasto lub ulicę
                if city or street:
                    parts = []
                    if city:
                        parts.append(city)
                    if street:
                        street_part = street
                        if house_number:
                            street_part += f" {house_number}"
                        parts.append(street_part)
                    
                    formatted_address = ", ".join(parts)
                    
                    # Unikaj duplikatów
                    if formatted_address not in seen:
                        seen.add(formatted_address)
                        formatted_results.append({
                            "display_name": formatted_address,
                            "lat": result.get("lat"),
                            "lon": result.get("lon"),
                            "address": address
                        })
            
            return formatted_results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")
