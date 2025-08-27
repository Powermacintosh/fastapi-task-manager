from typing import Annotated
from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_fastapi_connect, Task
from .crud import TaskCRUD


async def task_by_id(
    task_id: Annotated[str, Path],
    session: AsyncSession = Depends(db_fastapi_connect.scoped_session_dependency),
) -> Task:
    """
    Получает задачу по ID.

    param task_id: ID задачи, которую нужно получить.
    param session: Асинхронная сессия базы данных.
    return: Задача, если найдена.
    raises HTTPException: Если задача не найдена.
    """
    task = await TaskCRUD.get_task(session=session, task_id=task_id)
    if task is not None:
        return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Задача {task_id} не найдена!',
    )