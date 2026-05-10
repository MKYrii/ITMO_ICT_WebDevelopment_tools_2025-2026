# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    username: str = Field(unique=True, index=True)
    full_name: str
    password_hash: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    owned_tasks: List["Task"] = Relationship(back_populates="owner")
    task_assignments: List["UserTaskAssignment"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    __tablename__ = "task"

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_user_id: int = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: TaskPriority = Field(default=TaskPriority.medium)
    status: TaskStatus = Field(default=TaskStatus.todo)
    estimated_minutes: Optional[int] = None
    recurrence_rule: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    owner: User = Relationship(back_populates="owned_tasks")
    assignments: List["UserTaskAssignment"] = Relationship(back_populates="task")
    task_tags: List["TaskTag"] = Relationship(back_populates="task")


class UserTaskAssignment(SQLModel, table=True):
    __tablename__ = "user_task_assignment"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    task_id: int = Field(foreign_key="task.id")
    comment: Optional[str] = None
    assigned_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    user: User = Relationship(back_populates="task_assignments")
    task: Task = Relationship(back_populates="assignments")


class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    color: Optional[str] = None

    # Relationships
    task_tags: List["TaskTag"] = Relationship(back_populates="tag")


class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    tag_id: int = Field(foreign_key="tag.id")
    is_primary: bool = Field(default=False)

    # Relationships
    task: Task = Relationship(back_populates="task_tags")
    tag: Tag = Relationship(back_populates="task_tags")