from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime

from app.db.session import get_db
from app.routers.deps import get_current_active_user
from app.models.user import User
from app.models.enterprise import Enterprise
from app.models.equipment import Equipment
from app.models.order import ProductionOrder
from app.models.warehouse import WarehouseItem

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    # Base Stats
    total_orders = db.query(ProductionOrder).count()
    completed_orders = db.query(ProductionOrder).filter(ProductionOrder.status == "completed").count()
    problem_orders = db.query(ProductionOrder).filter(ProductionOrder.status == "problem").count()
    
    # KPI 1: OTD
    current_time = datetime.now()
    overdue_orders = db.query(ProductionOrder).filter(
        ProductionOrder.status != "completed",
        ProductionOrder.due_date < current_time
    ).count()
    
    # KPI 2: Equipment
    total_equipment = db.query(Equipment).count()
    operational_equipment = db.query(Equipment).filter(Equipment.status == "operational").count()
    availability_pct = (operational_equipment / total_equipment * 100) if total_equipment > 0 else 0
    
    # KPI 3: Warehouse & Finance (Real Calculation)
    warehouse_total_qty = db.query(func.sum(WarehouseItem.quantity)).scalar() or 0
    low_stock_count = db.query(WarehouseItem).filter(WarehouseItem.quantity < 50).count()
    
    # Calculate total value = SUM(quantity * price)
    # SQLite might need raw SQL or python loop if simple func.sum(a*b) is tricky with ORM in some versions,
    # but let's try python loop for safety and precision.
    all_items = db.query(WarehouseItem).all()
    estimated_value = sum(item.quantity * item.price for item in all_items)

    stats = {
        "factories": db.query(Enterprise).count(),
        "equipment": total_equipment,
        "orders_active": db.query(ProductionOrder).filter(ProductionOrder.status == "in_progress").count(),
        "warehouse_total": warehouse_total_qty,
        "estimated_value": estimated_value
    }
    
    # Chart 1: Equipment Status
    eq_status = db.query(Equipment.status, func.count(Equipment.id)).group_by(Equipment.status).all()
    status_data = {"operational": 0, "broken": 0, "maintenance": 0}
    for status, count in eq_status:
        status_data[status] = count
        
    # Chart 2: Top Products
    product_stats = db.query(
        ProductionOrder.product_name, 
        func.sum(ProductionOrder.quantity)
    ).group_by(ProductionOrder.product_name).order_by(desc(func.sum(ProductionOrder.quantity))).limit(5).all()
    
    prod_labels = [p[0] for p in product_stats]
    prod_values = [p[1] for p in product_stats]

    # KPI Percentages
    kpi_quality = 100 - (problem_orders / total_orders * 100) if total_orders > 0 else 100
    kpi_completion = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    recent_orders = db.query(ProductionOrder).order_by(ProductionOrder.created_date.desc()).limit(6).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "status_data": status_data,
        "prod_labels": prod_labels,
        "prod_values": prod_values,
        "recent_orders": recent_orders,
        "kpi": {
            "quality": round(kpi_quality, 1),
            "completion": round(kpi_completion, 1),
            "problems": problem_orders,
            "overdue": overdue_orders,
            "availability": round(availability_pct, 1),
            "low_stock": low_stock_count
        }
    })
