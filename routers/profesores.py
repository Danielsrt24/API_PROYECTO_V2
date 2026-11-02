from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from database import get_db
from models.profesor import Profesor, ProfesorCreate, ProfesorUpdate, ProfesorResponse
from models.usuario import Usuario
from core.authorization import require_roles

router = APIRouter(prefix="/profesores", tags=["Profesores"])

@router.get("/", response_model=List[ProfesorResponse])
def listar_profesores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.exec(
        select(Profesor).where(Profesor.estado == True).offset(skip).limit(limit)
    ).all()

@router.get("/{profesor_id}", response_model=ProfesorResponse)
def obtener_profesor(profesor_id: int, db: Session = Depends(get_db)):
    profesor = db.get(Profesor, profesor_id)
    if not profesor or not profesor.estado:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

@router.post(
    "/",
    response_model=ProfesorResponse,
    status_code=201,
    dependencies=[Depends(require_roles("Director", "Subdirector"))],
)
def crear_profesor(data: ProfesorCreate, db: Session = Depends(get_db)):
    if data.id_usuario is not None:
        usuario = db.get(Usuario, data.id_usuario)
        if not usuario or not usuario.estado or usuario.rol != "Profesor":
            raise HTTPException(status_code=400, detail="El usuario vinculado no es un profesor activo")
        if db.exec(select(Profesor).where(Profesor.id_usuario == data.id_usuario)).first():
            raise HTTPException(status_code=400, detail="El usuario ya tiene un perfil de profesor")

    nuevo = Profesor(
        id_usuario=data.id_usuario,
        nombre=data.nombre,
        email=data.email,
        estado=True
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put(
    "/{profesor_id}",
    response_model=ProfesorResponse,
    dependencies=[Depends(require_roles("Director", "Subdirector"))],
)
def editar_profesor(profesor_id: int, data: ProfesorUpdate, db: Session = Depends(get_db)):
    profesor = db.get(Profesor, profesor_id)
    if not profesor or not profesor.estado:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profesor, field, value)

    db.add(profesor)
    db.commit()
    db.refresh(profesor)
    return profesor

@router.delete(
    "/{profesor_id}",
    dependencies=[Depends(require_roles("Director", "Subdirector"))],
)
def eliminar_profesor(profesor_id: int, db: Session = Depends(get_db)):
    profesor = db.get(Profesor, profesor_id)
    if not profesor or not profesor.estado:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    profesor.estado = False
    db.add(profesor)
    db.commit()
    
    return {"message": "Profesor desactivado"}