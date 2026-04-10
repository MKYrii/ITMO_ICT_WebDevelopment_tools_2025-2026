from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.db import get_session
from app.dependencies import get_current_user
from app.models import User, Task, UserTaskAssignment
from app.schemas import TaskAssignmentCreate, TaskAssignmentResponse

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/", response_model=TaskAssignmentResponse)
def create_assignment(
        payload: TaskAssignmentCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskAssignmentResponse:
    # Проверяем, что задача существует и принадлежит текущему пользователю
    task = session.get(Task, payload.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can assign users")

    # Проверяем, что пользователь существует
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Проверяем, не существует ли уже назначение
    existing = session.exec(
        select(UserTaskAssignment).where(
            UserTaskAssignment.task_id == payload.task_id,
            UserTaskAssignment.user_id == payload.user_id
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already assigned to this task")

    assignment = UserTaskAssignment(
        task_id=payload.task_id,
        user_id=payload.user_id,
        comment=payload.comment,
    )
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment


@router.get("/task/{task_id}", response_model=list[TaskAssignmentResponse])
def get_task_assignments(
        task_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> list[TaskAssignmentResponse]:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can view assignments")

    assignments = session.exec(
        select(UserTaskAssignment).where(UserTaskAssignment.task_id == task_id)
    ).all()
    return assignments


@router.get("/user/{user_id}", response_model=list[TaskAssignmentResponse])
def get_user_assignments(
        user_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> list[TaskAssignmentResponse]:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot view other user's assignments")

    assignments = session.exec(
        select(UserTaskAssignment).where(UserTaskAssignment.user_id == user_id)
    ).all()
    return assignments


@router.patch("/{assignment_id}", response_model=TaskAssignmentResponse)
def update_assignment_comment(
        assignment_id: int,
        comment: str,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
) -> TaskAssignmentResponse:
    assignment = session.get(UserTaskAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    task = session.get(Task, assignment.task_id)
    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can update assignments")

    assignment.comment = comment
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}")
def delete_assignment(
        assignment_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    assignment = session.get(UserTaskAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    task = session.get(Task, assignment.task_id)
    if task.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only task owner can delete assignments")

    session.delete(assignment)
    session.commit()
    return {"status": "deleted"}