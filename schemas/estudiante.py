from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class EstudianteBase(BaseModel):
    nombre: str
    apellido: str
    cedula: str
    fecha_nacimiento: Optional[date] = None
    sexo: str
    id_seccion: int

class EstudianteCreate(EstudianteBase):
    pass

class EstudianteResponse(EstudianteBase):
    id_estudiante: int

    model_config = ConfigDict(from_attributes=True)
