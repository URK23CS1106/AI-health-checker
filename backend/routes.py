from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import save_prediction, get_history, create_user, get_user
from ml_model.predictor import predict_disease

# SECURITY CONSTANTS
SECRET_KEY = "pulse_ai_super_secret_key" # In production, reading from ENV is better!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

router = APIRouter()

# --- Security Functions ---
def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


# --- Request Models ---
class UserRegister(BaseModel):
    username: str
    password: str

class SymptomInput(BaseModel):
    symptoms: str


# --- Endpoints ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    hashed_pw = get_password_hash(user.password)
    user_id = create_user(user.username, hashed_pw)
    if not user_id:
        raise HTTPException(status_code=400, detail="Username already registered")
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/predict")
async def predict(data: SymptomInput, current_user: dict = Depends(get_current_user)):
    symptoms_text = data.symptoms
    if not symptoms_text or len(symptoms_text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Please provide a valid symptom description.")
    
    predictions = predict_disease(symptoms_text)
    save_prediction(symptoms_text, predictions, current_user['id'])
    
    return {"predictions": predictions}

@router.get("/history")
async def fetch_history(current_user: dict = Depends(get_current_user)):
    history = get_history(current_user['id'])
    return {"history": history}

@router.post("/chat")
async def chat(data: SymptomInput, current_user: dict = Depends(get_current_user)):
    symptoms_text = data.symptoms
    if not symptoms_text or len(symptoms_text.strip()) < 3:
        return {"bot_response": "I didn't quite catch that. Could you describe your symptoms more clearly?"}
    
    try:
        predictions = predict_disease(symptoms_text)
        save_prediction(symptoms_text, predictions, current_user['id'])
        
        if not predictions:
            bot_response = "I couldn't identify any specific diseases based on those symptoms. If you feel unwell, please consult a real doctor."
        else:
            top_disease = predictions[0]
            bot_response = f"Based on your symptoms, there's a {top_disease['probability']*100:.1f}% chance it might be **{top_disease['disease']}**. {top_disease['description']}"
            
        return {
            "bot_response": bot_response,
            "predictions": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
