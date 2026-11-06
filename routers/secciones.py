from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from typing import Annotated, List

from database import get_db
from models.seccion import Seccion, SeccionCreate, SeccionUpdate, SeccionResponse
from core.authorization import require_roles

router = APIRouter(prefix="/secciones", tags=["Secciones"])

@router.get("/", response_model=List[SeccionResponse])
def listar_secciones(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0)] = 100,
    db: Session = Depends(get_db),
):
    return db.exec(
        select(Seccion).where(Seccion.estado == True).offset(skip).limit(limit)
    ).all()

@router.get("/{seccion_id}", response_model=SeccionResponse)
def obtener_seccion(seccion_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    seccion = db.get(Seccion, seccion_id)
    if not seccion or not seccion.estado:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    return seccion

@router.post(
    "/",
    response_model=SeccionResponse,
    status_code=201,
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def crear_seccion(data: SeccionCreate, db: Session = Depends(get_db)):
    stmt = select(Seccion).where(
        Seccion.nombre == data.nombre,
        Seccion.estado == True
    )
    if db.exec(stmt).first():
        raise HTTPException(
            status_code=409,
            detail="Ese nombre de sección ya está en uso. Ingresa uno diferente.",
        )
    
    nuevo = Seccion(**data.model_dump(), estado=True)
    db.add(nuevo)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ese nombre de sección ya está en uso. Ingresa uno diferente.",
        ) from exc
    db.refresh(nuevo)
    return nuevo

@router.put(
    "/{seccion_id}",
    response_model=SeccionResponse,
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def editar_seccion(
    seccion_id: Annotated[int, Path(gt=0)],
    data: SeccionUpdate,
    db: Session = Depends(get_db),
):
    seccion = db.get(Seccion, seccion_id)
    if not seccion or not seccion.estado:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    
    update_data = data.model_dump(exclude_unset=True)
    final_data = {
        "nombre": update_data.get("nombre", seccion.nombre),
        "nivel": update_data.get("nivel", seccion.nivel),
        "letra": update_data.get("letra", seccion.letra),
    }
    if db.exec(
        select(Seccion).where(
            Seccion.nombre == final_data["nombre"],
            Seccion.estado == True,
            Seccion.id_seccion != seccion_id,
        )
    ).first():
        raise HTTPException(
            status_code=409,
            detail="Ese nombre de sección ya está en uso. Ingresa uno diferente.",
        )

    for key, value in update_data.items():
        setattr(seccion, key, value)
        
    db.add(seccion)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ese nombre de sección ya está en uso. Ingresa uno diferente.",
        ) from exc
    db.refresh(seccion)
    return seccion

@router.delete(
    "/{seccion_id}",
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def eliminar_seccion(seccion_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    seccion = db.get(Seccion, seccion_id)
    if not seccion or not seccion.estado:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    seccion.estado = False
    db.add(seccion)
    db.commit()
    return {"message": "Sección desactivada"}