from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from database import get_db
from models.distribucion import Distribucion, DistribucionCreate, DistribucionUpdate, DistribucionResponse
from models.profesor import Profesor
from models.materia import Materia
from models.seccion import Seccion
from core.authorization import require_roles

router = APIRouter(prefix="/distribucion", tags=["Distribución"])

@router.get("/", response_model=List[DistribucionResponse])
def listar_distribucion(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.exec(select(Distribucion).where(Distribucion.estado == True).offset(skip).limit(limit)).all()

@router.post(
    "/",
    response_model=DistribucionResponse,
    status_code=201,
    dependencies=[Depends(require_roles("Director"))],
)
def crear_distribucion(data: DistribucionCreate, db: Session = Depends(get_db)):
    referencias = (
        (Profesor, data.id_profesor, "Profesor"),
        (Materia, data.id_materia, "Materia"),
        (Seccion, data.id_seccion, "Sección"),
    )
    for model, record_id, label in referencias:
        record = db.get(model, record_id)
        if not record or not record.estado:
            raise HTTPException(status_code=404, detail=f"{label} no encontrado")

    stmt = select(Distribucion).where(
        Distribucion.id_profesor == data.id_profesor,
        Distribucion.id_materia == data.id_materia,
        Distribucion.id_seccion == data.id_seccion,
        Distribucion.estado == True
    )
    if db.exec(stmt).first():
        raise HTTPException(status_code=400, detail="Esta asignación ya existe")
    
    nuevo = Distribucion(**data.model_dump(), estado=True)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put(
    "/{dist_id}",
    response_model=DistribucionResponse,
    dependencies=[Depends(require_roles("Director"))],
)
def editar_distribucion(dist_id: int, data: DistribucionUpdate, db: Session = Depends(get_db)):
    dist = db.get(Distribucion, dist_id)
    if not dist or not dist.estado:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    update_data = data.model_dump(exclude_unset=True)
    final_data = {
        "id_profesor": update_data.get("id_profesor", dist.id_profesor),
        "id_materia": update_data.get("id_materia", dist.id_materia),
        "id_seccion": update_data.get("id_seccion", dist.id_seccion),
    }
    referencias = (
        (Profesor, final_data["id_profesor"], "Profesor"),
        (Materia, final_data["id_materia"], "Materia"),
        (Seccion, final_data["id_seccion"], "Sección"),
    )
    for model, record_id, label in referencias:
        record = db.get(model, record_id)
        if not record or not record.estado:
            raise HTTPException(status_code=404, detail=f"{label} no encontrado")

    stmt = select(Distribucion).where(
        Distribucion.id_profesor == final_data["id_profesor"],
        Distribucion.id_materia == final_data["id_materia"],
        Distribucion.id_seccion == final_data["id_seccion"],
        Distribucion.estado == True,
        Distribucion.id_distribucion != dist_id,
    )
    if db.exec(stmt).first():
        raise HTTPException(status_code=400, detail="Esta asignación ya existe")

    for key, value in update_data.items():
        setattr(dist, key, value)
        
    db.add(dist)
    db.commit()
    db.refresh(dist)
    return dist

@router.delete(
    "/{dist_id}",
    dependencies=[Depends(require_roles("Director"))],
)
def eliminar_distribucion(dist_id: int, db: Session = Depends(get_db)):
    dist = db.get(Distribucion, dist_id)
    if not dist or not dist.estado:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    dist.estado = False
    db.add(dist)
    db.commit()
    return {"message": "Asignación desactivada"}