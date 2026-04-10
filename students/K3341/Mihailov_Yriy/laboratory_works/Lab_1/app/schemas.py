from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel

from app.models import TaskStatus, TaskPriority


class PasswordChange(SQLModel):
    old_password: str
    new_password: str


class LoginRequest(SQLModel):
    username: str
    password: str


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"



# ========== User Schemas ==========
class UserBase(SQLModel):
    username: str
    email: str
    full_name: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


UserRead = UserResponse


class UserUpdate(SQLModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserListResponse(SQLModel):
    users: List[UserResponse]
    total: int


# ========== Tag Schemas ==========
class TagBase(SQLModel):
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True


class TagUpdate(SQLModel):
    name: Optional[str] = None
    color: Optional[str] = None


# ========== Task Schemas ==========
class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.todo
    estimated_minutes: Optional[int] = None
    recurrence_rule: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    estimated_minutes: Optional[int] = None
    recurrence_rule: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    owner_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(SQLModel):
    tasks: List[TaskResponse]
    total: int


# ========== UserTaskAssignment Schemas ==========
class TaskAssignmentCreate(SQLModel):
    task_id: int
    user_id: int
    comment: Optional[str] = None


class TaskAssignmentResponse(SQLModel):
    id: int
    task_id: int
    user_id: int
    comment: Optional[str]
    assigned_at: datetime

    class Config:
        from_attributes = True


# ========== TaskTag Schemas ==========
class TaskTagCreate(SQLModel):
    task_id: int
    tag_id: int
    is_primary: bool = False


class TaskTagResponse(SQLModel):
    task_id: int
    tag_id: int
    is_primary: bool
    tag: TagResponse

    class Config:
        from_attributes = True


# ========== Time Log Schemas ==========
class TimeLogBase(SQLModel):
    task_id: int
    duration_minutes: int
    notes: Optional[str] = None


class TimeLogCreate(TimeLogBase):
    pass


class TimeLogResponse(TimeLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Daily Schedule Schemas ==========
class DailyScheduleCreate(SQLModel):
    task_id: int
    scheduled_date: date
    scheduled_time: Optional[str] = None
    order_index: int = 0


class DailyScheduleResponse(SQLModel):
    id: int
    task_id: int
    scheduled_date: date
    scheduled_time: Optional[str]
    order_index: int
    task: TaskResponse

    class Config:
        from_attributes = True


# ========== Analytics Schemas ==========
class TimeAnalyticsResponse(SQLModel):
    total_minutes: int
    by_priority: dict  # {priority: minutes}
    by_tag: dict  # {tag_name: minutes}
    by_date: dict  # {date: minutes}


# (TaskResponse -> UserResponse)
TaskResponse.model_rebuild()