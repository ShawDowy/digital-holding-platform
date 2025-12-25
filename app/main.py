from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from app.db.base import Base
from app.db.session import engine, get_db
from app.routers import auth, dashboard, enterprises, equipment, orders, warehouse, api, users, logs
from app.models.user import User
# Import all models to ensure tables are created
from app.models.enterprise import Enterprise
from app.models.order import ProductionOrder
from app.models.operation import ProductionOperation, DefectLog
from app.models.repair import RepairLog
from app.models.log import SystemLog
from app.core.security import get_password_hash
from app.core.iot_simulator import start_iot_simulation

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Цифровая платформа холдинга")

@app.on_event("startup")
async def startup_event():
    start_iot_simulation()


# Ensure static folder exists
import os
if not os.path.exists("app/static"):
    os.makedirs("app/static")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(enterprises.router, tags=["enterprises"])
app.include_router(equipment.router, tags=["equipment"])
app.include_router(orders.router, tags=["orders"])
app.include_router(warehouse.router, tags=["warehouse"])
app.include_router(users.router, tags=["users"])
app.include_router(logs.router, tags=["logs"])
app.include_router(api.router, prefix="/api", tags=["api"])

# Exception Handler for 401 Unauthorized
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/auth/login")
    return await http_exception_handler(request, exc)

@app.on_event("startup")
def create_initial_data():
    db = next(get_db())
    # Create default users if not exist
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(
            username="admin", 
            hashed_password=get_password_hash("admin"), 
            role="admin", 
            full_name="Системный Администратор"
        ))
    if not db.query(User).filter(User.username == "manager").first():
        db.add(User(
            username="manager", 
            hashed_password=get_password_hash("manager"), 
            role="manager", 
            full_name="Иван Петров (Менеджер)"
        ))
    if not db.query(User).filter(User.username == "operator").first():
        db.add(User(
            username="operator", 
            hashed_password=get_password_hash("operator"), 
            role="operator", 
            full_name="Алексей Сидоров (Оператор)"
        ))
    try:
        db.commit()
    except:
        db.rollback()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
