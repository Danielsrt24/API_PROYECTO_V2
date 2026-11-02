"""
Modelo de Usuario para la API
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
import re
from pydantic import ConfigDict, field_validator

ROLES_USUARIO = ("Director", "Subdirector", "Secretaria", "Profesor")


def _texto_requerido(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Este campo debe ser texto")
    value = value.strip()
    if not value:
        raise ValueError("Este campo es obligatorio")
    return value


def _validar_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Debe ser una dirección de correo válida")
    value = value.strip()
    if not value:
        return None
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
        raise ValueError("Debe ser una dirección de correo válida")
    return value

   # PRUEBA DE GIT DANI
class UsuarioBase(SQLModel):
    username: str = Field(index=True, unique=True, min_length=1, max_length=50)
    nombre: str = Field(min_length=1, max_length=150)
    rol: str = Field(min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)

    @field_validator("username", "nombre", mode="before")
    @classmethod
    def validar_textos_requeridos(cls, value: str) -> str:
        return _texto_requerido(value)

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, value: str) -> str:
        if value not in ROLES_USUARIO:
            raise ValueError("Rol no válido")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def validar_correo(cls, value: Optional[str]) -> Optional[str]:
        return _validar_email(value)

class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password")
    @classmethod
    def validar_password_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña excede el límite admitido")
        return value

class UsuarioUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    email: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    estado: Optional[bool] = None

    @field_validator("estado", mode="before")
    @classmethod
    def validar_estado(cls, value: Optional[bool]) -> Optional[bool]:
        if value is None:
            raise ValueError("El estado no puede ser nulo")
        return value

    @field_validator("nombre", mode="before")
    @classmethod
    def validar_nombre(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("El nombre no puede ser nulo")
        return _texto_requerido(value)

    @field_validator("email", mode="before")
    @classmethod
    def validar_correo(cls, value: Optional[str]) -> Optional[str]:
        return _validar_email(value)

    @field_validator("password", mode="before")
    @classmethod
    def validar_password_bcrypt(cls, value: Optional[str]) -> Optional[str]:
        if value == "":
            return None
        if value is not None and (
            not isinstance(value, str) or len(value.encode("utf-8")) > 72
        ):
            raise ValueError("La contraseña excede el límite admitido")
        return value

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    estado: bool
    fecha_registro: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"
    
    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(max_length=255)
    estado: bool = Field(default=True)
    
    fecha_registro: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    __table_args__ = {"extend_existing": True}