from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.dependencies import get_current_user
from app.models import User, Task, UserTaskAssignment, TaskTag, Tag
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
        payload: TaskCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskResponse:
    task = Task(
        owner_user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        deadline=payload.deadline,
        priority=payload.priority,
        status=payload.status,
        estimated_minutes=payload.estimated_minutes,
        recurrence_rule=payload.recurrence_rule,
    )
    session.add(task)
    session.flush()  # чтобы получить task.id

    # Добавляем теги
    if payload.tag_ids:
        for tag_id in payload.tag_ids:
            tag = session.get(Tag, tag_id)
            if tag:
                task_tag = TaskTag(task_id=task.id, tag_id=tag_id)
                session.add(task_tag)

    # Назначаем пользователей
    if payload.assigned_user_ids:
        for user_id in payload.assigned_user_ids:
            assignment = UserTaskAssignment(
                user_id=user_id,
                task_id=task.id,
                comment=None
            )
            session.add(assignment)

    session.commit()
    session.refresh(task)

    # Загружаем связи для ответа
    task.tags = session.exec(
        select(TaskTag).where(TaskTag.task_id == task.id)
    ).all()
    task.assignments = session.exec(
        select(UserTaskAssignment).where(UserTaskAssignment.task_id == task.id)
    ).all()

    return task


@router.get("/", response_model=TaskListResponse)
def list_tasks(
        skip: int = 0,
        limit: int = 100,
        status: str = None,
        priority: str = None,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskListResponse:
    query = select(Task).where(Task.owner_user_id == current_user.id)

    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)

    tasks = session.exec(query.offset(skip).limit(limit)).all()
    total = len(session.exec(query).all())

    return TaskListResponse(tasks=tasks, total=total)


@router.get("/assigned-to-me", response_model=TaskListResponse)
def tasks_assigned_to_me(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskListResponse:
    query = select(Task).join(UserTaskAssignment).where(
        UserTaskAssignment.user_id == current_user.id
    )
    tasks = session.exec(query.offset(skip).limit(limit)).all()
    total = len(session.exec(query).all())

    return TaskListResponse(tasks=tasks, total=total)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskResponse:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверяем доступ: владелец или назначенный пользователь
    if task.owner_user_id != current_user.id:
        assignment = session.exec(
            select(UserTaskAssignment).where(
                UserTaskAssignment.task_id == task_id,
                UserTaskAssignment.user_id == current_user.id
            )
        ).first()
        if not assignment:
            raise HTTPException(status_code=403, detail="Access denied")

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
        task_id: int,
        payload: TaskUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskResponse:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can update task")

    update_data = payload.model_dump(exclude_unset=True)

    # Обновляем простые поля
    for field, value in update_data.items():
        if field not in ["tag_ids", "assigned_user_ids"] and value is not None:
            setattr(task, field, value)

    # Обновляем теги
    if payload.tag_ids is not None:
        # Удаляем старые связи
        old_tags = session.exec(select(TaskTag).where(TaskTag.task_id == task_id)).all()
        for old in old_tags:
            session.delete(old)

        # Добавляем новые
        for tag_id in payload.tag_ids:
            tag = session.get(Tag, tag_id)
            if tag:
                task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
                session.add(task_tag)

    # Обновляем назначения
    if payload.assigned_user_ids is not None:
        old_assignments = session.exec(
            select(UserTaskAssignment).where(UserTaskAssignment.task_id == task_id)
        ).all()
        for old in old_assignments:
            session.delete(old)

        for user_id in payload.assigned_user_ids:
            assignment = UserTaskAssignment(user_id=user_id, task_id=task_id)
            session.add(assignment)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete task")

    session.delete(task)
    session.commit()

    return {"status": "deleted"}