from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.usuarios import router as usuarios_router
from routers.materias import router as materias_router
from routers.permisos import router as permisos_router
from routers.distribucion import router as distribucion_router
from routers.horario import router as horario_router
from routers.profesores import router as profesores_router
from routers.secciones import router as secciones_router  # ✅ NUEVO

app = FastAPI(
    title="Sistema INDA API",
    description="API para el sistema de gestión académica INDA",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(usuarios_router, prefix="/api")
app.include_router(materias_router, prefix="/api")
app.include_router(permisos_router, prefix="/api")
app.include_router(distribucion_router, prefix="/api")
app.include_router(horario_router, prefix="/api")
app.include_router(profesores_router, prefix="/api")
app.include_router(secciones_router, prefix="/api")  # ✅ NUEVO

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de INDA", "status": "running"}