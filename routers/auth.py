from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import get_db
from models.usuario import Usuario
from core.security import create_access_token
from core.helper import verify_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.exec(select(Usuario).where(Usuario.username == form.username)).first()
    
    if not usuario or not usuario.estado:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if not verify_password(form.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = create_access_token({"sub": usuario.username, "rol": usuario.rol})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id_usuario,
            "username": usuario.username,
            "rol": usuario.rol
        }
    }