from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.dependencies import get_current_user
from app.models import User, Task, Tag, TaskTag
from app.schemas import TaskTagCreate, TaskTagResponse, TagResponse, TaskResponse

router = APIRouter(prefix="/task-tags", tags=["TaskTags"])


@router.post("/", response_model=TaskTagResponse)
def add_tag_to_task(
        payload: TaskTagCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskTagResponse:
    # Проверяем задачу
    task = session.get(Task, payload.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can add tags")

    # Проверяем тег
    tag = session.get(Tag, payload.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Проверяем дубликат
    existing = session.exec(
        select(TaskTag).where(
            TaskTag.task_id == payload.task_id,
            TaskTag.tag_id == payload.tag_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already attached")

    task_tag = TaskTag(
        task_id=payload.task_id,
        tag_id=payload.tag_id,
        is_primary=payload.is_primary,
    )
    session.add(task_tag)
    session.commit()
    session.refresh(task_tag)
    return task_tag


@router.get("/task/{task_id}", response_model=List[TagResponse])
def get_task_tags(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> List[TagResponse]:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    task_tags = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id)
    ).all()

    tags = []
    for tt in task_tags:
        tag = session.get(Tag, tt.tag_id)
        if tag:
            tags.append(tag)

    return tags


@router.get("/tag/{tag_id}", response_model=List[TaskResponse])
def get_tag_tasks(
        tag_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> List[TaskResponse]:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    task_tags = session.exec(
        select(TaskTag).where(TaskTag.tag_id == tag_id)
    ).all()

    tasks = []
    for tt in task_tags:
        task = session.get(Task, tt.task_id)
        if task and task.owner_user_id == current_user.id:
            tasks.append(task)

    return tasks


@router.delete("/{task_id}/{tag_id}")
def remove_tag_from_task(
        task_id: int,
        tag_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> dict:
    task = session.get(Task, task_id)
    if not task or task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    task_tag = session.exec(
        select(TaskTag).where(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_id
        )
    ).first()

    if not task_tag:
        raise HTTPException(status_code=404, detail="Task-tag relation not found")

    session.delete(task_tag)
    session.commit()
    return {"status": "deleted"}