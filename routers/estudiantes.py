from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.estudiante import Estudiante
# IMPORTANTE: Solo importa Create y Response. Eliminamos Update que causaba error.
from schemas.estudiante import EstudianteCreate, EstudianteResponse 

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])

# 1. LISTAR
@router.get("/", response_model=List[EstudianteResponse])
def get_estudiantes(id_seccion: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Estudiante)
    if id_seccion is not None:
        query = query.filter(Estudiante.id_seccion == id_seccion)
    return query.all()

# 2. CREAR
@router.post("/", response_model=EstudianteResponse, status_code=status.HTTP_201_CREATED)
def create_estudiante(estudiante: EstudianteCreate, db: Session = Depends(get_db)):
    nuevo_estudiante = Estudiante(**estudiante.model_dump())
    db.add(nuevo_estudiante)
    db.commit()
    db.refresh(nuevo_estudiante)
    return nuevo_estudiante

# 3. OBTENER UNO POR ID
@router.get("/{id}", response_model=EstudianteResponse)
def get_estudiante_by_id(id: int, db: Session = Depends(get_db)):
    estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

# 4. EDITAR (PUT) - ARREGLA EL ERROR 500 AL GUARDAR CAMBIOS
@router.put("/{id}", response_model=EstudianteResponse)
def update_estudiante(id: int, estudiante_data: EstudianteCreate, db: Session = Depends(get_db)):
    db_estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == id).first()
    if not db_estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
    # Actualizar campos dinámicamente
    for key, value in estudiante_data.dict().items():
        setattr(db_estudiante, key, value)
        
    db.commit()
    db.refresh(db_estudiante)
    return db_estudiante

# 5. ELIMINAR (DELETE) - ARREGLA EL ERROR 404 AL BORRAR
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_estudiante(id: int, db: Session = Depends(get_db)):
    db_estudiante = db.query(Estudiante).filter(Estudiante.id_estudiante == id).first()
    if not db_estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
    db.delete(db_estudiante)
    db.commit()
    return None
