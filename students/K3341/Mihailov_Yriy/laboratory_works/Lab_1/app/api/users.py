from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate, PasswordChange
from app.core.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserRead)
def register(
        payload: UserCreate,
        session: Session = Depends(get_session)
) -> UserRead:
    exists = session.exec(
        select(User).where((User.username == payload.username) | (User.email == payload.email))
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user


@router.get("/", response_model=list[UserRead])
def list_users(
        session: Session = Depends(get_session),
        _: User = Depends(get_current_user)
) -> list[UserRead]:
    return session.exec(select(User)).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
        user_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> UserRead:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
        user_id: int,
        payload: UserUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> UserRead:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot update other users")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email:
        existing = session.exec(select(User).where(User.email == payload.email)).first()
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already taken")
        user.email = payload.email

    if payload.full_name:
        user.full_name = payload.full_name

    if payload.is_active is not None:
        user.is_active = payload.is_active

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/change-password")
def change_password(
        payload: PasswordChange,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    session.add(current_user)
    session.commit()
    return {"status": "password updated"}