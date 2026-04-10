from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.dependencies import get_current_user
from app.models import User, Task, Tag, TaskTag
from app.schemas import TaskTagCreate, TaskTagResponse

router = APIRouter(prefix="/task-tags", tags=["TaskTags"])


@router.post("/", response_model=TaskTagResponse)
def add_tag_to_task(
        payload: TaskTagCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskTagResponse:
    # Проверяем доступ к задаче
    task = session.get(Task, payload.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can add tags")

    # Проверяем существование тега
    tag = session.get(Tag, payload.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Проверяем, не привязан ли уже тег
    existing = session.exec(
        select(TaskTag).where(
            TaskTag.task_id == payload.task_id,
            TaskTag.tag_id == payload.tag_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already attached to this task")

    task_tag = TaskTag(
        task_id=payload.task_id,
        tag_id=payload.tag_id,
        is_primary=payload.is_primary,
    )
    session.add(task_tag)
    session.commit()
    session.refresh(task_tag)
    return task_tag


@router.get("/task/{task_id}", response_model=list[TaskTagResponse])
def get_task_tags(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> list[TaskTagResponse]:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        # Проверяем, назначен ли пользователь на задачу
        assignment = session.exec(
            select(UserTaskAssignment).where(
                UserTaskAssignment.task_id == task_id,
                UserTaskAssignment.user_id == current_user.id
            )
        ).first()
        if not assignment:
            raise HTTPException(status_code=403, detail="Access denied")

    task_tags = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id)
    ).all()
    return task_tags


@router.get("/tag/{tag_id}", response_model=list[TaskTagResponse])
def get_tag_tasks(
        tag_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> list[TaskTagResponse]:
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Возвращаем только задачи, доступные текущему пользователю
    task_tags = session.exec(
        select(TaskTag).where(TaskTag.tag_id == tag_id)
    ).all()

    # Фильтруем по доступным задачам
    accessible = []
    for tt in task_tags:
        task = session.get(Task, tt.task_id)
        if task.owner_user_id == current_user.id:
            accessible.append(tt)
        else:
            assignment = session.exec(
                select(UserTaskAssignment).where(
                    UserTaskAssignment.task_id == tt.task_id,
                    UserTaskAssignment.user_id == current_user.id
                )
            ).first()
            if assignment:
                accessible.append(tt)

    return accessible


@router.patch("/{task_id}/{tag_id}", response_model=TaskTagResponse)
def set_primary_tag(
        task_id: int,
        tag_id: int,
        is_primary: bool,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskTagResponse:
    task = session.get(Task, task_id)
    if not task or task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can set primary tag")

    task_tag = session.exec(
        select(TaskTag).where(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_id
        )
    ).first()

    if not task_tag:
        raise HTTPException(status_code=404, detail="Task-tag relation not found")

    task_tag.is_primary = is_primary
    session.add(task_tag)
    session.commit()
    session.refresh(task_tag)
    return task_tag


@router.delete("/{task_id}/{tag_id}")
def remove_tag_from_task(
        task_id: int,
        tag_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task or task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can remove tags")

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