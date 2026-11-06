from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from typing import Annotated, List
from datetime import datetime, timezone

from database import get_db
from models.materia import Materia, MateriaCreate, MateriaUpdate, MateriaResponse
from core.authorization import require_roles

router = APIRouter(prefix="/materias", tags=["Materias"])

@router.get("/", response_model=List[MateriaResponse])
def listar_materias(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0)] = 100,
    db: Session = Depends(get_db),
):
    return db.exec(
        select(Materia).where(Materia.estado == True).offset(skip).limit(limit)
    ).all()

@router.get("/{materia_id}", response_model=MateriaResponse)
def obtener_materia(materia_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    materia = db.get(Materia, materia_id)
    if not materia or not materia.estado:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return materia

@router.post(
    "/",
    response_model=MateriaResponse,
    status_code=201,
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def crear_materia(data: MateriaCreate, db: Session = Depends(get_db)):
    if db.exec(select(Materia).where(Materia.codigo == data.codigo)).first():
        raise HTTPException(
            status_code=409,
            detail="Ese código de materia ya está en uso. Ingresa uno diferente.",
        )
    
    nueva = Materia(
        **data.model_dump(),
        estado=True,
        fecha_creacion=datetime.now(timezone.utc)
    )
    db.add(nueva)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ese código de materia ya está en uso. Ingresa uno diferente.",
        ) from exc
    db.refresh(nueva)
    return nueva

@router.put(
    "/{materia_id}",
    response_model=MateriaResponse,
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def editar_materia(
    materia_id: Annotated[int, Path(gt=0)],
    data: MateriaUpdate,
    db: Session = Depends(get_db),
):
    materia = db.get(Materia, materia_id)
    if not materia or not materia.estado:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    
    update_data = data.model_dump(exclude_unset=True)
    if "codigo" in update_data and db.exec(
        select(Materia).where(
            Materia.codigo == update_data["codigo"],
            Materia.id_materia != materia_id,
        )
    ).first():
        raise HTTPException(
            status_code=409,
            detail="Ese código de materia ya está en uso. Ingresa uno diferente.",
        )

    for key, value in update_data.items():
        setattr(materia, key, value)
        
    db.add(materia)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ese código de materia ya está en uso. Ingresa uno diferente.",
        ) from exc
    db.refresh(materia)
    return materia

@router.delete(
    "/{materia_id}",
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def eliminar_materia(materia_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    materia = db.get(Materia, materia_id)
    if not materia or not materia.estado:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    materia.estado = False
    db.add(materia)
    db.commit()
    return {"message": "Materia desactivada"}