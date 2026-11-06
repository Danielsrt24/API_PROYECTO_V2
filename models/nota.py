from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal

class Nota(SQLModel, table=True):
    __tablename__ = "notas"
    
    id_nota: Optional[int] = Field(default=None, primary_key=True)
    id_estudiante: int = Field(gt=0, foreign_key="estudiantes.id_estudiante")
    id_materia: int = Field(gt=0, foreign_key="materias.id_materia")
    id_seccion: int = Field(gt=0, foreign_key="secciones.id_seccion")
    calificacion: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2, ge=0, le=10
    )
    periodo: Optional[str] = Field(default=None, max_length=20)
    id_usuario_registro: int = Field(gt=0, foreign_key="usuarios.id_usuario")
    fecha_registro: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fecha_modificacion: Optional[datetime] = Field(default=None)