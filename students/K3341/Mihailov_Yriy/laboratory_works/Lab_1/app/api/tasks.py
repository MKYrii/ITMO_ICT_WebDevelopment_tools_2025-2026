from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from typing import Optional, List

from app.db import get_session
from app.dependencies import get_current_user
from app.models import User, Task, TaskTag
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, TaskWithTagsResponse, \
    TaskListWithTagsResponse

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
    session.commit()
    session.refresh(task)
    return task


@router.get("/with_tags", response_model=TaskListWithTagsResponse)
def list_tasks_with_tags(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        status: Optional[str] = None,
        priority: Optional[str] = None,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskListWithTagsResponse:
    # Загружаем задачу и сразу подтягиваем теги через промежуточную таблицу
    query = (
        select(Task)
        .where(Task.owner_user_id == current_user.id)
        .options(selectinload(Task.task_tags).selectinload(TaskTag.tag))
    )

    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)

    tasks_result = session.exec(query.offset(skip).limit(limit)).all()

    # Формируем ответ с "плоским" списком тегов
    formatted_tasks = []
    for task in tasks_result:
        # Извлекаем сами объекты Tag из связей TaskTag
        flat_tags = [tt.tag for tt in task.task_tags]

        # Создаем модель ответа, подменяя пустой список tags
        task_out = TaskWithTagsResponse.model_validate(task)
        task_out.tags = flat_tags
        formatted_tasks.append(task_out)

    # Считаем общее количество
    total = session.scalar(
        select(func.count()).select_from(Task).where(Task.owner_user_id == current_user.id)
    )

    return TaskListWithTagsResponse(tasks=formatted_tasks, total=total)


@router.get("/{task_id}/with_tags", response_model=TaskWithTagsResponse)
def get_task_with_tags(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskWithTagsResponse:
    query = (
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.task_tags).selectinload(TaskTag.tag))
    )
    task = session.exec(query).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Выпрямляем список тегов для ответа
    flat_tags = [tt.tag for tt in task.task_tags]

    response = TaskWithTagsResponse.model_validate(task)
    response.tags = flat_tags

    return response


@router.get("/", response_model=TaskListResponse)
def list_tasks(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        status: Optional[str] = None,
        priority: Optional[str] = None,
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


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskResponse:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
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
    for field, value in update_data.items():
        if value is not None:
            setattr(task, field, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> dict:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete task")

    session.delete(task)
    session.commit()
    return {"status": "deleted"}