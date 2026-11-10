from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Estudiante(SQLModel, table=True):
    __tablename__ = "estudiantes"
    
    id_estudiante: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150)
    apellido: str = Field(max_length=150)
    cedula: str = Field(index=True, unique=True, max_length=20)
    fecha_nacimiento: Optional[date] = Field(default=None)
    sexo: str = Field(max_length=1)
    id_seccion: int = Field(foreign_key="secciones.id_seccion")
    # ✅ SOLO LOS CAMPOS QUE EXISTEN EN TU BD
