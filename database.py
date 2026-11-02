"""
Configuración de la base de datos para FastAPI + SQLModel + MySQL
"""
from sqlmodel import SQLModel, create_engine, Session

# 🔗 URL de conexión a MySQL
# Formato: mysql+pymysql://usuario:contraseña@host:puerto/base_de_datos
# (Si tu root de XAMPP no tiene contraseña, déjalo vacío después de los dos puntos)
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/inda_db"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=False)

# Función para crear las tablas (se puede llamar al inicio si se desea)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# ✅ Dependencia para obtener la sesión de la base de datos en los routers
def get_db():
    with Session(engine) as session:
        yield session