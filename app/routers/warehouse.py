from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.routers.deps import get_current_active_user, get_manager_user
from app.models.warehouse import WarehouseItem
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/warehouse", response_class=HTMLResponse)
async def list_warehouse(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    items = db.query(WarehouseItem).all()
    # Calculate total value per item for display
    for item in items:
        item.total_value = item.quantity * item.price
        
    return templates.TemplateResponse("warehouse.html", {
        "request": request,
        "user": user,
        "items": items
    })

@router.post("/warehouse")
async def add_warehouse_item(
    product_code: str = Form(...),
    product_name: str = Form(...),
    quantity: float = Form(...),
    price: float = Form(...),
    unit: str = Form(...),
    location: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_manager_user)
):
    if quantity <= 0:
        return RedirectResponse(url="/warehouse?error=Количество+должно+быть+больше+нуля", status_code=303)
    if price < 0:
        return RedirectResponse(url="/warehouse?error=Цена+не+может+быть+отрицательной", status_code=303)

    item = db.query(WarehouseItem).filter(WarehouseItem.product_code == product_code).first()
    if item:
        # Weighted average price calculation (Moving Average)
        total_old = item.quantity * item.price
        total_new = quantity * price
        item.quantity += quantity
        item.price = (total_old + total_new) / item.quantity
    else:
        new_item = WarehouseItem(
            product_code=product_code,
            product_name=product_name,
            quantity=quantity,
            price=price,
            unit=unit,
            location=location
        )
        db.add(new_item)
    
    db.commit()
    return RedirectResponse(url="/warehouse", status_code=303)

@router.post("/warehouse/{item_id}/ship")
async def ship_warehouse_item(
    item_id: str,
    amount: float = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_manager_user)
):
    if amount <= 0:
        return RedirectResponse(url="/warehouse?error=Нельзя+списать+отрицательное+количество+или+ноль", status_code=303)

    item = db.query(WarehouseItem).filter(WarehouseItem.id == item_id).first()
    if item:
        if item.quantity >= amount:
            item.quantity -= amount
            db.commit()
        else:
            return RedirectResponse(url=f"/warehouse?error=Ошибка:+На+складе+всего+{item.quantity}+ед.", status_code=303)
            
    return RedirectResponse(url="/warehouse", status_code=303)
