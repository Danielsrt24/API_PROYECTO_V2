from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from pydantic import ConfigDict, field_validator

class MateriaBase(SQLModel):
    codigo: str = Field(min_length=1, max_length=20, unique=True)
    nombre: str = Field(min_length=1, max_length=100)
    creditos: int = Field(default=0)

    @field_validator("codigo", "nombre", mode="before")
    @classmethod
    def validar_textos(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Este campo debe ser texto")
        value = value.strip()
        if not value:
            raise ValueError("Este campo es obligatorio")
        return value

class MateriaCreate(MateriaBase):
    pass

class MateriaUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    codigo: Optional[str] = Field(default=None, min_length=1, max_length=20)
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    creditos: Optional[int] = None

    @field_validator("codigo", "nombre", mode="before")
    @classmethod
    def validar_textos(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("Este campo no puede ser nulo")
        if not isinstance(value, str):
            raise ValueError("Este campo debe ser texto")
        value = value.strip()
        if not value:
            raise ValueError("Este campo es obligatorio")
        return value

    @field_validator("creditos", mode="before")
    @classmethod
    def validar_creditos(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            raise ValueError("Los créditos no pueden ser nulos")
        return value

class MateriaResponse(MateriaBase):
    id_materia: int
    estado: bool
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Materia(MateriaBase, table=True):
    __tablename__ = "materias"
    
    id_materia: Optional[int] = Field(default=None, primary_key=True)
    estado: bool = Field(default=True)
    fecha_creacion: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    __table_args__ = {"extend_existing": True}