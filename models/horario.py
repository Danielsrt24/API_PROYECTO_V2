from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import time
from pydantic import ConfigDict, field_validator

class HorarioBase(SQLModel):
    id_distribucion: int = Field(gt=0, foreign_key="distribucion.id_distribucion")
    dia: str = Field(min_length=1, max_length=20)
    hora_inicio: time
    hora_fin: time
    aula: Optional[str] = Field(default=None, max_length=50)

    @field_validator("dia")
    @classmethod
    def validar_dia(cls, value: str) -> str:
        if value not in {"Lunes", "Martes", "Miércoles", "Jueves", "Viernes"}:
            raise ValueError("Día de la semana no válido")
        return value

    @field_validator("aula", mode="before")
    @classmethod
    def normalizar_aula(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not isinstance(value, str):
            raise ValueError("El aula debe ser texto")
        return value.strip() if value is not None else None

class HorarioCreate(HorarioBase):
    pass

class HorarioUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    dia: Optional[str] = Field(default=None, min_length=1, max_length=20)
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    aula: Optional[str] = Field(default=None, max_length=50)

    @field_validator("dia")
    @classmethod
    def validar_dia(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            raise ValueError("El día no puede ser nulo")
        if value not in {"Lunes", "Martes", "Miércoles", "Jueves", "Viernes"}:
            raise ValueError("Día de la semana no válido")
        return value

    @field_validator("hora_inicio", "hora_fin", mode="before")
    @classmethod
    def validar_horas_no_nulas(cls, value: Optional[time]) -> Optional[time]:
        if value is None:
            raise ValueError("La hora no puede ser nula")
        return value

    @field_validator("aula", mode="before")
    @classmethod
    def normalizar_aula(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not isinstance(value, str):
            raise ValueError("El aula debe ser texto")
        return value.strip() if value is not None else None

class HorarioResponse(HorarioBase):
    id_horario: int
    estado: bool
    model_config = ConfigDict(from_attributes=True)

class Horario(HorarioBase, table=True):
    __tablename__ = "horario"
    id_horario: Optional[int] = Field(default=None, primary_key=True)
    estado: bool = Field(default=True)
    __table_args__ = {"extend_existing": True} # ✅ Esto evita el error de reload