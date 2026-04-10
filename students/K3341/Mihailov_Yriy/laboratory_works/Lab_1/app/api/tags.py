from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.dependencies import get_current_user
from app.models import User, Tag
from app.schemas import TagCreate, TagUpdate, TagResponse

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.post("/", response_model=TagResponse)
def create_tag(
        payload: TagCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TagResponse:
    existing = session.exec(select(Tag).where(Tag.name == payload.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")

    tag = Tag(name=payload.name, color=payload.color)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.get("/", response_model=list[TagResponse])
def list_tags(
        session: Session = Depends(get_session),
        _: User = Depends(get_current_user),
) -> list[TagResponse]:
    return session.exec(select(Tag)).all()


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
        tag_id: int,
        session: Session = Depends(get_session),
        _: User = Depends(get_current_user),
) -> TagResponse:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.patch("/{tag_id}", response_model=TagResponse)
def update_tag(
        tag_id: int,
        payload: TagUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TagResponse:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if payload.name:
        existing = session.exec(select(Tag).where(Tag.name == payload.name)).first()
        if existing and existing.id != tag_id:
            raise HTTPException(status_code=400, detail="Tag name already taken")
        tag.name = payload.name

    if payload.color is not None:
        tag.color = payload.color

    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}")
def delete_tag(
        tag_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    session.delete(tag)
    session.commit()
    return {"status": "deleted"}