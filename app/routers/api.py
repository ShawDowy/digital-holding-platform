from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.routers.deps import get_admin_user
from app.models.enterprise import Enterprise
from app.models.equipment import Equipment
from app.models.order import ProductionOrder
from app.models.warehouse import WarehouseItem
from app.models.user import User
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/init-data")
async def init_test_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user)
):
    # Clear existing BUSINESS data
    db.query(ProductionOrder).delete()
    db.query(Equipment).delete()
    db.query(Enterprise).delete()
    db.query(WarehouseItem).delete()
    db.commit()

    # Create Enterprises
    ent1 = Enterprise(
        id=str(uuid.uuid4()),
        name="🏔️ Добывающее предприятие №1", type="добывающее", region="Урал", description="Добыча железной руды открытым способом"
    )
    ent2 = Enterprise(
        id=str(uuid.uuid4()),
        name="🏭 Перерабатывающий завод №1", type="перерабатывающее", region="Сибирь", description="Обогащение руды и выплавка металла"
    )
    db.add(ent1); db.add(ent2); db.commit()

    # Create Equipment
    eq1 = Equipment(tag="EQ-001", name="Экскаватор карьерный CAT-7495", type="heavy_machinery", enterprise_id=ent1.id, status="operational")
    eq2 = Equipment(tag="EQ-002", name="Дробилка щековая СМД-110", type="processing", enterprise_id=ent2.id, status="maintenance")
    eq3 = Equipment(tag="EQ-003", name="Конвейер ленточный магистральный", type="transport", enterprise_id=ent2.id, status="broken")
    db.add(eq1); db.add(eq2); db.add(eq3); db.commit()

    # Create Orders with Prices
    order1 = ProductionOrder(
        order_number="PO-2024-001", product_code="RAW-IRON", product_name="Железная руда", 
        quantity=500.0, price_per_unit=120.0, enterprise_id=ent1.id, status="completed"
    )
    order2 = ProductionOrder(
        order_number="PO-2024-002", product_code="STEEL-BAR", product_name="Стальная заготовка", 
        quantity=120.0, price_per_unit=850.0, enterprise_id=ent2.id, status="in_progress"
    )
    db.add(order1); db.add(order2); db.commit()
    
    # Init Warehouse (from completed orders)
    wh_item = WarehouseItem(
        product_code="RAW-IRON", product_name="Железная руда", 
        quantity=500.0, price=120.0, unit="т", location="Склад сырья №1"
    )
    db.add(wh_item)
    
    # Ensure Users
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", hashed_password=get_password_hash("admin"), role="admin", full_name="Системный Администратор"))
    if not db.query(User).filter(User.username == "manager").first():
        db.add(User(username="manager", hashed_password=get_password_hash("manager"), role="manager", full_name="Иван Петров (Менеджер)"))
    if not db.query(User).filter(User.username == "operator").first():
        db.add(User(username="operator", hashed_password=get_password_hash("operator"), role="operator", full_name="Алексей Сидоров (Оператор)"))
        
    db.commit()
    return RedirectResponse(url="/auth/login", status_code=303)

@router.post("/clear-data")
async def clear_data(
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user)
):
    # Clear existing BUSINESS data
    db.query(ProductionOrder).delete()
    db.query(Equipment).delete()
    db.query(Enterprise).delete()
    db.query(WarehouseItem).delete()
    db.commit()
    return RedirectResponse(url="/auth/login", status_code=303)
