from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, select
from typing import Annotated, List
from datetime import time

from database import get_db
from models.horario import Horario, HorarioCreate, HorarioUpdate, HorarioResponse
from models.distribucion import Distribucion
from core.authorization import require_roles

router = APIRouter(prefix="/horario", tags=["Horario"])

@router.get("/", response_model=List[HorarioResponse])
def listar_horarios(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0)] = 100,
    db: Session = Depends(get_db),
):
    return db.exec(
        select(Horario).where(Horario.estado == True).offset(skip).limit(limit)
    ).all()

@router.get("/{horario_id}", response_model=HorarioResponse)
def obtener_horario(horario_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    horario = db.get(Horario, horario_id)
    if not horario or not horario.estado:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    return horario

def validar_choque(
    db: Session,
    id_distribucion: int,
    dia: str,
    hora_inicio: time,
    hora_fin: time,
    exclude_id: int | None = None
) -> bool:
    distribucion_actual = db.get(Distribucion, id_distribucion)
    if not distribucion_actual:
        return False
    
    statement = select(Horario).where(
        Horario.estado == True,
        Horario.dia == dia,
        Horario.hora_inicio < hora_fin,
        Horario.hora_fin > hora_inicio
    )
    
    if exclude_id is not None:
        statement = statement.where(Horario.id_horario != exclude_id)
    
    horarios_existentes = db.exec(statement).all()
    
    for h in horarios_existentes:
        dist_existente = db.get(Distribucion, h.id_distribucion)
        if not dist_existente:
            continue
        
        if dist_existente.id_profesor == distribucion_actual.id_profesor:
            return True
        if dist_existente.id_seccion == distribucion_actual.id_seccion:
            return True
    
    return False

@router.post(
    "/",
    response_model=HorarioResponse,
    status_code=201,
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def crear_horario(data: HorarioCreate, db: Session = Depends(get_db)):
    distribucion = db.get(Distribucion, data.id_distribucion)
    if not distribucion or not distribucion.estado:
        raise HTTPException(status_code=404, detail="Distribución no encontrada")
    
    if data.hora_inicio >= data.hora_fin:
        raise HTTPException(status_code=400, detail="La hora de inicio debe ser menor que la hora fin")
    
    if validar_choque(db, data.id_distribucion, data.dia, data.hora_inicio, data.hora_fin):
        raise HTTPException(
            status_code=409,
            detail="Hay un choque de horario: el profesor o la sección ya tienen clase en ese horario"
        )
    
    nuevo = Horario(
        id_distribucion=data.id_distribucion,
        dia=data.dia,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        aula=data.aula,
        estado=True
    )
    
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put(
    "/{horario_id}",
    response_model=HorarioResponse,
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def editar_horario(
    horario_id: Annotated[int, Path(gt=0)],
    data: HorarioUpdate,
    db: Session = Depends(get_db),
):
    horario = db.get(Horario, horario_id)
    if not horario or not horario.estado:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    update_data = data.model_dump(exclude_unset=True)
    if any(update_data.get(field) is None for field in ("dia", "hora_inicio", "hora_fin") if field in update_data):
        raise HTTPException(status_code=422, detail="Día y horas son campos obligatorios")
    for field, value in update_data.items():
        setattr(horario, field, value)

    distribucion = db.get(Distribucion, horario.id_distribucion)
    if not distribucion or not distribucion.estado:
        raise HTTPException(status_code=404, detail="Distribución no encontrada")
    if horario.hora_inicio >= horario.hora_fin:
        raise HTTPException(status_code=400, detail="La hora de inicio debe ser menor que la hora fin")
    
    if validar_choque(db, horario.id_distribucion, horario.dia, horario.hora_inicio, horario.hora_fin, exclude_id=horario_id):
        raise HTTPException(
            status_code=409,
            detail="Hay un choque de horario: el profesor o la sección ya tienen clase en ese horario"
        )
    
    db.add(horario)
    db.commit()
    db.refresh(horario)
    return horario

@router.delete(
    "/{horario_id}",
    dependencies=[Depends(require_roles("Director", "Subdirector", "Secretaria"))],
)
def eliminar_horario(horario_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    horario = db.get(Horario, horario_id)
    if not horario or not horario.estado:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    
    horario.estado = False
    db.add(horario)
    db.commit()
    
    return {"message": "Horario desactivado"}

@router.get("/seccion/{seccion_id}", response_model=List[HorarioResponse])
def horario_por_seccion(seccion_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    distribuciones = db.exec(
        select(Distribucion).where(Distribucion.id_seccion == seccion_id, Distribucion.estado == True)
    ).all()
    
    dist_ids = [d.id_distribucion for d in distribuciones]
    if not dist_ids:
        return []
    
    statement = select(Horario).where(
        Horario.id_distribucion.in_(dist_ids),
        Horario.estado == True
    ).order_by(Horario.dia, Horario.hora_inicio)
    
    return db.exec(statement).all()  # ✅ CORREGIDO: Agregado .all()

@router.get("/profesor/{profesor_id}", response_model=List[HorarioResponse])
def horario_por_profesor(profesor_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    distribuciones = db.exec(
        select(Distribucion).where(Distribucion.id_profesor == profesor_id, Distribucion.estado == True)
    ).all()
    
    dist_ids = [d.id_distribucion for d in distribuciones]
    if not dist_ids:
        return []
    
    statement = select(Horario).where(
        Horario.id_distribucion.in_(dist_ids),
        Horario.estado == True
    ).order_by(Horario.dia, Horario.hora_inicio)
    
    return db.exec(statement).all()