from sqlmodel import SQLModel, Field
from typing import Optional

class EstudianteSeccion(SQLModel, table=True):
    __tablename__ = "estudiante_seccion"
    
    id_estudiante_seccion: Optional[int] = Field(default=None, primary_key=True)
    id_estudiante: int = Field(gt=0, foreign_key="estudiantes.id_estudiante")
    id_seccion: int = Field(gt=0, foreign_key="secciones.id_seccion")
    año_lectivo: str = Field(max_length=10)