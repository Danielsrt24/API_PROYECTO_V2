from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, select
from typing import Annotated, List
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.usuario import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioResponse
from core.helper import hash_password
from core.authorization import require_roles

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get(
    "/",
    response_model=List[UsuarioResponse],
    dependencies=[Depends(require_roles("Director", "Subdirector"))],
)
def listar_usuarios(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0)] = 100,
    db: Session = Depends(get_db),
):
    return db.exec(
        select(Usuario).where(Usuario.estado == True).offset(skip).limit(limit)
    ).all()

@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    dependencies=[Depends(require_roles("Director", "Subdirector"))],
)
def obtener_usuario(usuario_id: Annotated[int, Path(gt=0)], db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario or not usuario.estado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=201,
    dependencies=[Depends(require_roles("Director", "Subdirector"))],
)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    if db.exec(select(Usuario).where(Usuario.username == data.username)).first():
        raise HTTPException(
            status_code=409,
            detail="Ese nombre de usuario ya está en uso. Ingresa uno diferente.",
        )

    nuevo_usuario = Usuario(
        username=data.username,
        password_hash=hash_password(data.password),
        nombre=data.nombre,
        rol=data.rol,
        email=data.email,
        estado=True
    )
    db.add(nuevo_usuario)

    try:
        if data.rol == "Profesor":
            from models.profesor import Profesor

            db.flush()
            db.add(
                Profesor(
                    id_usuario=nuevo_usuario.id_usuario,
                    nombre=data.nombre,
                    email=data.email,
                    estado=True,
                )
            )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ese nombre de usuario ya está en uso. Ingresa uno diferente.",
        ) from exc

    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    dependencies=[Depends(require_roles("Director", "Subdirector"))],
)
def editar_usuario(
    usuario_id: Annotated[int, Path(gt=0)],
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    password = update_data.pop("password", None)
    for field, value in update_data.items():
        setattr(usuario, field, value)
    if password:
        usuario.password_hash = hash_password(password)

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/{usuario_id}")
def eliminar_usuario(
    usuario_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("Director")),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario or not usuario.estado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.id_usuario == current_user.id_usuario:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    usuario.estado = False
    db.add(usuario)
    db.commit()
    
    return {"message": "Usuario desactivado"}