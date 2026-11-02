import re
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from core.authorization import get_current_user
from database import get_db
from models.permiso import Permiso, PermisoCreate, PermisoResponse, PermisoUpdate
from models.profesor import Profesor
from models.usuario import Usuario

router = APIRouter(prefix="/permisos", tags=["Permisos"])

MEDIA_ROOT = Path(__file__).resolve().parents[2] / "web" / "media"
TIPOS_COMPROBANTE_PERMITIDOS = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/pdf",
}


def _obtener_profesor_usuario(db: Session, usuario: Usuario) -> Profesor:
    profesor = db.exec(
        select(Profesor).where(
            Profesor.id_usuario == usuario.id_usuario,
            Profesor.estado == True,
        )
    ).first()
    if profesor is None:
        raise HTTPException(
            status_code=400,
            detail="Tu usuario no tiene un perfil de profesor activo vinculado",
        )
    return profesor


def _validar_profesor_activo(db: Session, profesor_id: int) -> Profesor:
    profesor = db.get(Profesor, profesor_id)
    if profesor is None or not profesor.estado:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor


def _guardar_comprobante(archivo: UploadFile, profesor_id: int, fecha_inicio: date) -> str:
    if archivo.content_type not in TIPOS_COMPROBANTE_PERMITIDOS:
        raise HTTPException(
            status_code=422,
            detail="El comprobante debe ser JPG, PNG o PDF",
        )

    filename = Path(archivo.filename or "comprobante").name
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename) or "comprobante"
    relative_path = Path("comprobantes") / (
        f"permiso_{profesor_id}_{fecha_inicio}_{uuid.uuid4().hex}_{filename}"
    )
    destination = MEDIA_ROOT / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(archivo.file.read())
    return relative_path.as_posix()


def _eliminar_comprobante(relative_path: Optional[str]) -> None:
    if not relative_path:
        return
    path = (MEDIA_ROOT / relative_path).resolve()
    media_root = MEDIA_ROOT.resolve()
    if path.is_relative_to(media_root) and path.is_file():
        path.unlink()


@router.get("/", response_model=list[PermisoResponse])
def listar_permisos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    statement = select(Permiso).order_by(Permiso.fecha_inicio.desc())
    if current_user.rol == "Profesor":
        profesor = _obtener_profesor_usuario(db, current_user)
        statement = statement.where(Permiso.id_profesor == profesor.id_profesor)
    return db.exec(statement).all()


@router.post("/", response_model=PermisoResponse, status_code=201)
def crear_permiso(
    tipo_permiso: str = Form(...),
    fecha_inicio: date = Form(...),
    fecha_fin: date = Form(...),
    horas_afectadas: Decimal = Form(Decimal("0")),
    motivo: Optional[str] = Form(None),
    id_profesor: Optional[int] = Form(None),
    comprobante: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    data = PermisoCreate(
        id_profesor=id_profesor,
        tipo_permiso=tipo_permiso.strip(),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        horas_afectadas=horas_afectadas,
        motivo=motivo.strip() if motivo is not None else None,
    )

    if current_user.rol == "Profesor":
        profesor = _obtener_profesor_usuario(db, current_user)
    else:
        if data.id_profesor is None:
            raise HTTPException(status_code=422, detail="Debes seleccionar un profesor")
        profesor = _validar_profesor_activo(db, data.id_profesor)

    comprobante_path = _guardar_comprobante(
        comprobante,
        profesor.id_profesor,
        data.fecha_inicio,
    )
    permiso = Permiso(
        id_profesor=profesor.id_profesor,
        tipo_permiso=data.tipo_permiso,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        horas_afectadas=data.horas_afectadas,
        motivo=data.motivo,
        estado="pendiente",
        id_usuario_registro=current_user.id_usuario,
        comprobante=comprobante_path,
    )
    db.add(permiso)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        _eliminar_comprobante(comprobante_path)
        raise HTTPException(status_code=409, detail="No se pudo guardar el permiso") from exc
    db.refresh(permiso)
    return permiso


@router.put("/{permiso_id}", response_model=PermisoResponse)
def editar_permiso(
    permiso_id: int,
    tipo_permiso: Optional[str] = Form(None),
    fecha_inicio: Optional[date] = Form(None),
    fecha_fin: Optional[date] = Form(None),
    horas_afectadas: Optional[Decimal] = Form(None),
    motivo: Optional[str] = Form(None),
    estado: Optional[str] = Form(None),
    comprobante: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol == "Profesor":
        raise HTTPException(status_code=403, detail="No tienes permisos para editar permisos")

    permiso = db.get(Permiso, permiso_id)
    if permiso is None:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")

    update_values = {
        "tipo_permiso": tipo_permiso.strip() if tipo_permiso is not None else None,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "horas_afectadas": horas_afectadas,
        "motivo": motivo.strip() if motivo is not None else None,
        "estado": estado,
    }
    data = PermisoUpdate.model_validate(
        {key: value for key, value in update_values.items() if value is not None}
    )
    update_data = data.model_dump(exclude_unset=True)
    fecha_inicio_final = update_data.get("fecha_inicio", permiso.fecha_inicio)
    fecha_fin_final = update_data.get("fecha_fin", permiso.fecha_fin)
    if fecha_fin_final < fecha_inicio_final:
        raise HTTPException(
            status_code=422,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )
    for field, value in update_data.items():
        setattr(permiso, field, value)

    comprobante_anterior = permiso.comprobante
    comprobante_nuevo = None
    if comprobante is not None:
        comprobante_nuevo = _guardar_comprobante(
            comprobante,
            permiso.id_profesor,
            permiso.fecha_inicio,
        )
        permiso.comprobante = comprobante_nuevo

    db.add(permiso)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        _eliminar_comprobante(comprobante_nuevo)
        raise HTTPException(status_code=409, detail="No se pudo actualizar el permiso") from exc

    if comprobante_nuevo:
        _eliminar_comprobante(comprobante_anterior)
    db.refresh(permiso)
    return permiso


@router.delete("/{permiso_id}")
def eliminar_permiso(
    permiso_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if current_user.rol == "Profesor":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar permisos")

    permiso = db.get(Permiso, permiso_id)
    if permiso is None:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")

    comprobante = permiso.comprobante
    db.delete(permiso)
    db.commit()
    _eliminar_comprobante(comprobante)
    return {"message": "Permiso eliminado"}
