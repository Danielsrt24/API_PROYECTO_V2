from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime, timezone

class Estudiante(SQLModel, table=True):
    __tablename__ = "estudiantes"
    
    id_estudiante: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150)
    apellido: str = Field(max_length=150)
    cedula: str = Field(index=True, unique=True, max_length=20) # ✅ CEDULA
    fecha_nacimiento: Optional[date] = Field(default=None)
    sexo: str = Field(max_length=1)
    # ❌ ELIMINADO: estado_civil (No existe en tu BD)
    
    id_seccion: int = Field(foreign_key="secciones.id_seccion")
    #email: Optional[str] = Field(default=None, max_length=100)
    estado: bool = Field(default=True)
    #fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
