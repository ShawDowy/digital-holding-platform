from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.db.session import get_db
from app.routers.deps import get_current_active_user, get_admin_user
from app.models.equipment import Equipment
from app.models.repair import RepairLog
from app.models.enterprise import Enterprise
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/equipment", response_class=HTMLResponse)
async def list_equipment(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    equipment = db.query(Equipment).all()
    enterprises = db.query(Enterprise).all()
    return templates.TemplateResponse("equipment.html", {
        "request": request,
        "user": user,
        "equipment": equipment,
        "enterprises": enterprises
    })

@router.get("/equipment/{equipment_id}", response_class=HTMLResponse)
async def get_equipment_details(
    equipment_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not eq:
        return RedirectResponse(url="/equipment", status_code=303)
        
    return templates.TemplateResponse("equipment_detail.html", {
        "request": request,
        "user": user,
        "eq": eq
    })

@router.post("/equipment")
async def create_equipment(
    request: Request,
    name: str = Form(...),
    tag: str = Form(...),
    type: str = Form(...),
    enterprise_id: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user)
):
    new_eq = Equipment(
        tag=tag,
        name=name,
        type=type,
        enterprise_id=enterprise_id,
        status="operational"
    )
    db.add(new_eq)
    db.commit()
    return RedirectResponse(url="/equipment", status_code=303)

@router.post("/equipment/{equipment_id}/delete")
async def delete_equipment(
    equipment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user)
):
    db.query(Equipment).filter(Equipment.id == equipment_id).delete()
    db.commit()
    return RedirectResponse(url="/equipment", status_code=303)

@router.post("/equipment/{equipment_id}/status")
async def update_status(
    equipment_id: str,
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    eq = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if eq:
        eq.status = status
        db.commit()
        
    return RedirectResponse(url="/equipment", status_code=303)

@router.post("/equipment/{equipment_id}/repairs")
async def add_repair(
    equipment_id: str,
    description: str = Form(...),
    performed_by: str = Form(None),
    cost: float = Form(0.0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    repair = RepairLog(
        equipment_id=equipment_id,
        description=description,
        performed_by=performed_by,
        cost=cost,
        status="pending"
    )
    db.add(repair)
    db.commit()
    return RedirectResponse(url=f"/equipment/{equipment_id}", status_code=303)

@router.post("/repairs/{repair_id}/update")
async def update_repair(
    repair_id: str,
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    repair = db.query(RepairLog).filter(RepairLog.id == repair_id).first()
    if repair:
        repair.status = status
        if status == "completed" and not repair.end_date:
            repair.end_date = datetime.now()
            # Also update equipment last maintenance
            repair.equipment.last_maintenance = datetime.now()
            repair.equipment.status = "operational" # Assume fixed
            
        db.commit()
        return RedirectResponse(url=f"/equipment/{repair.equipment_id}", status_code=303)
        
    return RedirectResponse(url="/equipment", status_code=303)
