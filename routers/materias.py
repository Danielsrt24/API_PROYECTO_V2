from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timezone

from database import get_db
from models.materia import Materia, MateriaCreate, MateriaUpdate, MateriaResponse
from core.authorization import require_roles

router = APIRouter(prefix="/materias", tags=["Materias"])

@router.get("/", response_model=List[MateriaResponse])
def listar_materias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.exec(
        select(Materia).where(Materia.estado == True).offset(skip).limit(limit)
    ).all()

@router.get("/{materia_id}", response_model=MateriaResponse)
def obtener_materia(materia_id: int, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=400, detail="Ya existe una materia con ese código")
    
    nueva = Materia(
        **data.model_dump(),
        estado=True,
        fecha_creacion=datetime.now(timezone.utc)
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put(
    "/{materia_id}",
    response_model=MateriaResponse,
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def editar_materia(materia_id: int, data: MateriaUpdate, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=400, detail="Ya existe una materia con ese código")

    for key, value in update_data.items():
        setattr(materia, key, value)
        
    db.add(materia)
    db.commit()
    db.refresh(materia)
    return materia

@router.delete(
    "/{materia_id}",
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def eliminar_materia(materia_id: int, db: Session = Depends(get_db)):
    materia = db.get(Materia, materia_id)
    if not materia or not materia.estado:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    materia.estado = False
    db.add(materia)
    db.commit()
    return {"message": "Materia desactivada"}