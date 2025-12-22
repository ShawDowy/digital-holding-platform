from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.routers.deps import get_current_active_user, get_admin_user
from app.models.enterprise import Enterprise
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/enterprises", response_class=HTMLResponse)
async def list_enterprises(
    request: Request, 
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    enterprises = db.query(Enterprise).all()
    return templates.TemplateResponse("enterprises.html", {
        "request": request,
        "user": user,
        "enterprises": enterprises
    })

@router.post("/enterprises")
async def create_enterprise(
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    region: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_admin_user)  # Only admin can add factories
):
    new_enterprise = Enterprise(
        id=str(uuid.uuid4()),
        name=name,
        type=type,
        region=region,
        description=description
    )
    db.add(new_enterprise)
    db.commit()
    return RedirectResponse(url="/enterprises", status_code=303)

@router.get("/enterprises/{enterprise_id}", response_class=HTMLResponse)
async def enterprise_detail(
    enterprise_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    enterprise = db.query(Enterprise).filter(Enterprise.id == enterprise_id).first()
    return templates.TemplateResponse("enterprise_detail.html", {
        "request": request,
        "user": user,
        "enterprise": enterprise
    })
