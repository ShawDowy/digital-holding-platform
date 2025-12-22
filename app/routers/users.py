from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uuid

from app.db.session import get_db
from app.routers.deps import get_admin_user
from app.models.user import User
from app.core.security import get_password_hash

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    users = db.query(User).all()
    return templates.TemplateResponse("users.html", {
        "request": request,
        "user": current_user,
        "users": users
    })

@router.post("/users")
async def create_user(
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # Check if user exists
    if db.query(User).filter(User.username == username).first():
        return RedirectResponse(url="/users?error=Пользователь+уже+существует", status_code=303)
    
    new_user = User(
        username=username,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role
    )
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/users?success=Пользователь+создан", status_code=303)

@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # Prevent deleting yourself
    if user_id == current_user.id:
         return RedirectResponse(url="/users?error=Нельзя+удалить+себя", status_code=303)

    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    return RedirectResponse(url="/users", status_code=303)

