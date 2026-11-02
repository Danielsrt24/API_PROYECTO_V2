"""
Modelo de Profesor para la API
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
import re
from pydantic import ConfigDict, field_validator

class ProfesorBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=150)
    email: Optional[str] = Field(default=None, max_length=150)

    @field_validator("nombre", mode="before")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("El nombre debe ser texto")
        value = value.strip()
        if not value:
            raise ValueError("El nombre es obligatorio")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def validar_email(cls, value: Optional[str]) -> Optional[str]:
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

class ProfesorCreate(ProfesorBase):
    id_usuario: Optional[int] = Field(default=None, gt=0)

class ProfesorUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    email: Optional[str] = Field(default=None, max_length=150)

    @field_validator("nombre", mode="before")
    @classmethod
    def validar_nombre(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("El nombre no puede ser nulo")
        if not isinstance(value, str):
            raise ValueError("El nombre debe ser texto")
        value = value.strip()
        if not value:
            raise ValueError("El nombre es obligatorio")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def validar_email(cls, value: Optional[str]) -> Optional[str]:
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

class ProfesorResponse(ProfesorBase):
    id_profesor: int
    estado: bool
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Profesor(ProfesorBase, table=True):
    __tablename__ = "profesores"
    
    id_profesor: Optional[int] = Field(default=None, primary_key=True)
    estado: bool = Field(default=True)
    id_usuario: Optional[int] = Field(default=None)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    __table_args__ = {"extend_existing": True}