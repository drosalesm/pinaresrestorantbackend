from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db.database import get_db
from app.models.users import User
from app.utils.auth import verify_password, get_password_hash, create_access_token,decode_access_token
from fastapi import Form
from app.schemas.auth import UserCreate,UserUpdate
from app.auth.auth import get_current_user
from app.utils.utils import format_response
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")






@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    print('Entrando al modulo de autenticacion...')

    # Check if username OR email already exists
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario o correo electrónico ya están en uso")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, name=user.name,email=user.email, hashed_password=hashed_password, role=user.role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Usuario creado exitosamente", "user": {"id": new_user.id, "username": new_user.username,"name":new_user.name, "role": new_user.role}}


@router.post("/token")
def login_for_access_token(data: dict, db: Session = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/users")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        users = db.query(User).all()

        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        # Serialize the user data
        users_list = [{"id": user.id, "username": user.username, "name":user.name,"email": user.email,"role":user.role} for user in users]

        return {"message": "Users retrieved successfully", "users": users_list}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuario No Encontrado")

    # Update only the provided fields
    if user_data.username:
        existing_user.username = user_data.username
    if user_data.name:
        existing_user.name = user_data.name        
    if user_data.email:
        existing_user.email = user_data.email
    if user_data.role:
        existing_user.role = user_data.role

    db.commit()
    db.refresh(existing_user)

    return {"message": "Usuario actualizado exitosamente", "user": existing_user}





@router.get("/userDetails", summary="Retrieve a user by ID or username")
def get_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: int = Query(None, description="Filter user by ID"),
    username: str = Query(None, description="Filter user by username"),
):
    try:
        query = db.query(User)

        if user_id:
            query = query.filter(User.id == user_id)
        if username:
            query = query.filter(User.username == username)

        user = query.first()

        if not user:
            return format_response(404, "No se encontró el usuario")

        user_data = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }

        return format_response(200, "Usuario encontrado exitosamente", user_data)

    except Exception as e:
        print(e)
        return format_response(500, "Error interno del servidor")