from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.db.session import get_db
from app.routers.deps import get_current_active_user, get_manager_user, get_admin_user
from app.models.order import ProductionOrder
from app.models.enterprise import Enterprise
from app.models.warehouse import WarehouseItem
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/orders", response_class=HTMLResponse)
async def list_orders(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    orders = db.query(ProductionOrder).order_by(ProductionOrder.created_date.desc()).all()
    enterprises = db.query(Enterprise).all()
    return templates.TemplateResponse("orders.html", {
        "request": request,
        "user": user,
        "orders": orders,
        "enterprises": enterprises
    })

@router.post("/orders")
async def create_order(
    request: Request,
    product_name: str = Form(...),
    product_code: str = Form(...),
    quantity: float = Form(...),
    price_per_unit: float = Form(...),
    enterprise_id: str = Form(...),
    due_date: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_manager_user)
):
    if quantity <= 0:
        return RedirectResponse(url="/orders?error=Количество+должно+быть+больше+нуля", status_code=303)
    if price_per_unit < 0:
        return RedirectResponse(url="/orders?error=Цена+не+может+быть+отрицательной", status_code=303)

    parsed_date = None
    if due_date:
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            pass

    new_order = ProductionOrder(
        order_number=f"PO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}",
        product_name=product_name,
        product_code=product_code,
        quantity=quantity,
        price_per_unit=price_per_unit,
        enterprise_id=enterprise_id,
        due_date=parsed_date,
        status="new"
    )
    db.add(new_order)
    db.commit()
    return RedirectResponse(url="/orders", status_code=303)

@router.post("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        return RedirectResponse(url="/orders", status_code=303)
        
    previous_status = order.status
    order.status = status
    
    if status == "completed" and previous_status != "completed":
        # WMS Integration with Pricing
        wh_item = db.query(WarehouseItem).filter(WarehouseItem.product_code == order.product_code).first()
        if wh_item:
            # Weighted average price
            total_old = wh_item.quantity * wh_item.price
            total_new = order.quantity * order.price_per_unit
            wh_item.quantity += order.quantity
            wh_item.price = (total_old + total_new) / wh_item.quantity
        else:
            new_item = WarehouseItem(
                product_code=order.product_code,
                product_name=order.product_name,
                quantity=order.quantity,
                price=order.price_per_unit,
                unit="т"
            )
            db.add(new_item)
            
    db.commit()
    return RedirectResponse(url="/orders", status_code=303)

@router.post("/orders/{order_id}/problem")
async def report_order_problem(
    order_id: str,
    problem_details: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if order:
        order.status = "problem"
        order.problem_details = problem_details
        db.commit()
    return RedirectResponse(url="/orders", status_code=303)

@router.post("/orders/{order_id}/delete")
async def delete_order(
    order_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_manager_user)
):
    db.query(ProductionOrder).filter(ProductionOrder.id == order_id).delete()
    db.commit()
    return RedirectResponse(url="/orders", status_code=303)
