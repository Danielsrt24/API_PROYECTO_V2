from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict, field_validator, model_validator
from sqlmodel import Field, SQLModel

TIPOS_PERMISO = (
    "Permiso medico",
    "Permiso personal",
    "Permiso por duelo",
    "Permiso por maternidad",
    "Vacaciones",
    "Otro",
)
ESTADOS_PERMISO = ("pendiente", "aprobado", "rechazado")


class PermisoCreate(SQLModel):
    id_profesor: Optional[int] = Field(default=None, gt=0)
    tipo_permiso: str = Field(min_length=1, max_length=50)
    fecha_inicio: date
    fecha_fin: date
    horas_afectadas: Decimal = Field(
        default=Decimal("0"),
        max_digits=5,
        decimal_places=2,
        ge=0,
        le=24,
    )
    motivo: Optional[str] = None

    @field_validator("tipo_permiso")
    @classmethod
    def validar_tipo(cls, value: str) -> str:
        if value not in TIPOS_PERMISO:
            raise ValueError("Tipo de permiso no válido")
        return value

    @model_validator(mode="after")
    def validar_fechas(self) -> "PermisoCreate":
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio")
        return self


class PermisoUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    tipo_permiso: Optional[str] = Field(default=None, min_length=1, max_length=50)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    horas_afectadas: Optional[Decimal] = Field(
        default=None,
        max_digits=5,
        decimal_places=2,
        ge=0,
        le=24,
    )
    motivo: Optional[str] = None
    estado: Optional[str] = Field(default=None, max_length=20)

    @field_validator("tipo_permiso")
    @classmethod
    def validar_tipo(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in TIPOS_PERMISO:
            raise ValueError("Tipo de permiso no válido")
        return value

    @field_validator("fecha_inicio", "fecha_fin", "horas_afectadas", "estado", mode="before")
    @classmethod
    def validar_campos_no_nulos(cls, value: object) -> object:
        if value is None:
            raise ValueError("El campo no puede ser nulo")
        return value

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in ESTADOS_PERMISO:
            raise ValueError("Estado de permiso no válido")
        return value


class PermisoResponse(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id_permiso: int
    id_profesor: int = Field(gt=0)
    tipo_permiso: str
    fecha_inicio: date
    fecha_fin: date
    horas_afectadas: Optional[Decimal] = None
    motivo: Optional[str] = None
    estado: str
    id_usuario_registro: int
    fecha_registro: datetime
    comprobante: Optional[str] = None


class Permiso(SQLModel, table=True):
    __tablename__ = "permisos"

    id_permiso: Optional[int] = Field(default=None, primary_key=True)
    id_profesor: int
    tipo_permiso: str = Field(max_length=50)
    fecha_inicio: date
    fecha_fin: date
    horas_afectadas: Optional[Decimal] = Field(
        default=None,
        max_digits=5,
        decimal_places=2,
        ge=0,
        le=24,
    )
    motivo: Optional[str] = None
    estado: str = Field(default="pendiente", max_length=20)
    id_usuario_registro: int = Field(gt=0)
    fecha_registro: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    comprobante: Optional[str] = Field(default=None, max_length=255)
