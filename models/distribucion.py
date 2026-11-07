"""
Modelo de Distribución para la API
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import ConfigDict, field_validator

class DistribucionBase(SQLModel):
    id_profesor: int = Field(gt=0, foreign_key="profesores.id_profesor")
    id_materia: int = Field(gt=0, foreign_key="materias.id_materia")
    id_seccion: int = Field(gt=0, foreign_key="secciones.id_seccion")
    horas_semanales: int = Field(default=0, ge=0)

class DistribucionCreate(DistribucionBase):
    pass

class DistribucionUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    id_profesor: Optional[int] = Field(default=None, gt=0)
    id_materia: Optional[int] = Field(default=None, gt=0)
    id_seccion: Optional[int] = Field(default=None, gt=0)
    horas_semanales: Optional[int] = Field(default=None, ge=0)

    @field_validator("id_profesor", "id_materia", "id_seccion", "horas_semanales", mode="before")
    @classmethod
    def validar_valores_no_nulos(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            raise ValueError("Este campo no puede ser nulo")
        return value

class DistribucionResponse(DistribucionBase):
    id_distribucion: int
    estado: bool

    model_config = ConfigDict(from_attributes=True)

class Distribucion(DistribucionBase, table=True):
    __tablename__ = "distribucion"
    id_distribucion: Optional[int] = Field(default=None, primary_key=True)
    estado: bool = Field(default=True)

    __table_args__ = {"extend_existing": True}