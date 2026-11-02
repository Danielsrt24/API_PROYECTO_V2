from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import ConfigDict, field_validator

class SeccionBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    nivel: Optional[str] = Field(default=None, max_length=50)
    letra: Optional[str] = Field(default=None, max_length=10)

    @field_validator("nombre", mode="before")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("El nombre debe ser texto")
        value = value.strip()
        if not value:
            raise ValueError("El nombre es obligatorio")
        return value

    @field_validator("nivel", "letra", mode="before")
    @classmethod
    def normalizar_textos_opcionales(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not isinstance(value, str):
            raise ValueError("Este campo debe ser texto")
        return value.strip() if value is not None else None

class SeccionCreate(SeccionBase):
    pass

class SeccionUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    nivel: Optional[str] = Field(default=None, max_length=50)
    letra: Optional[str] = Field(default=None, max_length=10)

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

    @field_validator("nivel", "letra", mode="before")
    @classmethod
    def normalizar_textos_opcionales(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not isinstance(value, str):
            raise ValueError("Este campo debe ser texto")
        return value.strip() if value is not None else None

class SeccionResponse(SeccionBase):
    id_seccion: int
    estado: bool

    model_config = ConfigDict(from_attributes=True)

class Seccion(SeccionBase, table=True):
    __tablename__ = "secciones"
    
    id_seccion: Optional[int] = Field(default=None, primary_key=True)
    estado: bool = Field(default=True)
    
    __table_args__ = {"extend_existing": True}