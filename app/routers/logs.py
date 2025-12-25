from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.routers.deps import get_current_active_user
from app.models.user import User
from app.models.log import SystemLog

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/logs", response_class=HTMLResponse)
async def view_logs(
    request: Request, 
    module: str = None,
    user_search: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user)
):
    # Only Admin and Manager can view logs
    if user.role not in ['admin', 'manager']:
        return templates.TemplateResponse("base.html", {"request": request, "user": user, "error": "Access denied"})
        
    query = db.query(SystemLog)
    
    if module and module != "ALL":
        query = query.filter(SystemLog.module == module)
        
    if user_search:
        query = query.filter(SystemLog.username.contains(user_search))
        
    logs = query.order_by(SystemLog.timestamp.desc()).limit(200).all()
    
    # Get unique modules for filter
    modules = [m[0] for m in db.query(SystemLog.module).distinct().all()]
    
    return templates.TemplateResponse("logs.html", {
        "request": request,
        "user": user,
        "logs": logs,
        "modules": modules,
        "selected_module": module,
        "user_search": user_search
    })
