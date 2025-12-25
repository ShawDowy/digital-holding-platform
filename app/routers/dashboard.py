from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from datetime import datetime, timedelta

from app.db.session import get_db
from app.routers.deps import get_current_active_user
from app.models.user import User
from app.models.enterprise import Enterprise
from app.models.equipment import Equipment
from app.models.order import ProductionOrder
from app.models.warehouse import WarehouseItem
from app.models.operation import DefectLog

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

    # Chart 3: Defects Analysis
    defect_stats = db.query(
        DefectLog.reason,
        func.sum(DefectLog.quantity)
    ).group_by(DefectLog.reason).order_by(desc(func.sum(DefectLog.quantity))).all()
    
    defect_labels = [d[0] for d in defect_stats]
    defect_values = [d[1] for d in defect_stats]

    # Chart 4: Production Trend (Last 7 days)
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    # SQLite has limited date functions, so we'll fetch and process in python for simplicity and compatibility
    # Get all orders from last 7 days
    recent_trend_orders = db.query(ProductionOrder).filter(ProductionOrder.created_date >= seven_days_ago).all()
    
    trend_map = { (seven_days_ago + timedelta(days=i)): 0 for i in range(7) }
    
    for order in recent_trend_orders:
        o_date = order.created_date.date()
        if o_date in trend_map:
            trend_map[o_date] += order.quantity
            
    trend_labels = [d.strftime("%d.%m") for d in sorted(trend_map.keys())]
    trend_values = [trend_map[d] for d in sorted(trend_map.keys())]

    # KPI Percentages
    kpi_quality = 100 - (problem_orders / total_orders * 100) if total_orders > 0 else 100
    kpi_completion = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    recent_orders = db.query(ProductionOrder).order_by(ProductionOrder.created_date.desc()).limit(6).all()
    
    # Live Telemetry for Dashboard
    live_equipment = db.query(Equipment).order_by(Equipment.last_telemetry_update.desc()).limit(5).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "status_data": status_data,
        "prod_labels": prod_labels,
        "prod_values": prod_values,
        "defect_labels": defect_labels,
        "defect_values": defect_values,
        "trend_labels": trend_labels,
        "trend_values": trend_values,
        "recent_orders": recent_orders,
        "live_equipment": live_equipment,
        "kpi": {
            "quality": round(kpi_quality, 1),
            "completion": round(kpi_completion, 1),
            "problems": problem_orders,
            "overdue": overdue_orders,
            "availability": round(availability_pct, 1),
            "low_stock": low_stock_count
        }
    })
