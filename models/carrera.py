from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Carrera(SQLModel, table=True):
    __tablename__ = "carreras"
    
    id_carrera: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True, max_length=10)
    nombre: str = Field(max_length=100)
    estado: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))