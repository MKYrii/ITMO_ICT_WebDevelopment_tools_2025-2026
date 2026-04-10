from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.dependencies import get_current_user
from app.models import User, Task, UserTaskAssignment
from app.schemas import TaskAssignmentCreate, TaskAssignmentResponse, UserResponse, TaskResponse

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/", response_model=TaskAssignmentResponse)
def create_assignment(
        payload: TaskAssignmentCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskAssignmentResponse:
    task = session.get(Task, payload.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can assign users")

    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = session.exec(
        select(UserTaskAssignment).where(
            UserTaskAssignment.task_id == payload.task_id,
            UserTaskAssignment.user_id == payload.user_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already assigned")

    assignment = UserTaskAssignment(
        task_id=payload.task_id,
        user_id=payload.user_id,
        comment=payload.comment,
    )
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment


@router.get("/task/{task_id}", response_model=List[UserResponse])
def get_task_assignees(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> List[UserResponse]:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can view assignments")

    assignments = session.exec(
        select(UserTaskAssignment).where(UserTaskAssignment.task_id == task_id)
    ).all()

    users = []
    for ass in assignments:
        user = session.get(User, ass.user_id)
        if user:
            users.append(user)

    return users


@router.get("/user/{user_id}", response_model=List[TaskResponse])
def get_user_tasks(
        user_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> List[TaskResponse]:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot view other user's assignments")

    assignments = session.exec(
        select(UserTaskAssignment).where(UserTaskAssignment.user_id == user_id)
    ).all()

    tasks = []
    for ass in assignments:
        task = session.get(Task, ass.task_id)
        if task:
            tasks.append(task)

    return tasks


@router.delete("/{task_id}/{user_id}")
def remove_assignment(
        task_id: int,
        user_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> dict:
    task = session.get(Task, task_id)
    if not task or task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    assignment = session.exec(
        select(UserTaskAssignment).where(
            UserTaskAssignment.task_id == task_id,
            UserTaskAssignment.user_id == user_id
        )
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    session.delete(assignment)
    session.commit()
    return {"status": "deleted"}