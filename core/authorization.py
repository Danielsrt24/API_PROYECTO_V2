from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from config import settings
from database import get_db
from models.usuario import ROLES_USUARIO, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o sesión expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username = payload.get("sub")
        role = payload.get("rol")
        if not isinstance(username, str) or role not in ROLES_USUARIO:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = db.exec(select(Usuario).where(Usuario.username == username)).first()
    if user is None or not user.estado or user.rol != role:
        raise credentials_error
    return user


def require_roles(*allowed_roles: str) -> Callable:
    def role_dependency(
        current_user: Usuario = Depends(get_current_user),
    ) -> Usuario:
        if current_user.rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción",
            )
        return current_user

    return role_dependency
