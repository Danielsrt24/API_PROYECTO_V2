from sqlmodel import SQLModel, Field
from typing import Optional

class MateriaProfesor(SQLModel, table=True):
    __tablename__ = "materia_profesor"
    
    id_materia_profesor: Optional[int] = Field(default=None, primary_key=True)
    id_materia: int = Field(gt=0, foreign_key="materias.id_materia")
    id_profesor: int = Field(gt=0, foreign_key="profesores.id_profesor")