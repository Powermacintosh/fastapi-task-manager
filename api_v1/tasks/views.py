from typing import Annotated
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import db_fastapi_connect
from .crud import TaskCRUD
from .dependencies import task_by_id
from .schemas import (
    TaskCreate,
    SchemaTask,
    TaskUpdate,
    TaskUpdatePartial,
    TasksResponseSchema
)

router, router_list = APIRouter(tags=['Tasks']), APIRouter(tags=['Tasks'])


@router.post('/create', response_model=SchemaTask, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    session: AsyncSession = Depends(db_fastapi_connect.scoped_session_dependency)
):
    """
    Создает новую задачу.

    param task: Задача, которую нужно создать.
    param session: Асинхронная сессия базы данных.
    return: Созданная задача.
    raises HTTPException: При возникновении ошибки.
    """
    return await TaskCRUD.create_task(session=session, task=task)


@router.get('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def get_task(
    task: SchemaTask = Depends(task_by_id)
):
    """
    Получает задачу по ID.

    param task: Задача, которую нужно получить.
    return: Задача.
    """
    return task


@router.put('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def update_task(
    task_update: TaskUpdate,
    task: SchemaTask = Depends(task_by_id),
    session: AsyncSession = Depends(db_fastapi_connect.scoped_session_dependency),    
):
    """
    Полностью обновляет задачу по ID.

    param task_update: Обновленная задача.
    param task: Задача, которую нужно обновить.
    param session: Асинхронная сессия базы данных.
    return: Обновленная задача.
    raises HTTPException: При возникновении ошибки.
    """
    return await TaskCRUD.update_task(
        session=session,
        task=task,
        task_update=task_update
    )


@router.patch('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def update_partial_task(
    task_update: TaskUpdatePartial,
    task: SchemaTask = Depends(task_by_id),
    session: AsyncSession = Depends(db_fastapi_connect.scoped_session_dependency),    
):
    """
    Частично обновляет задачу по ID.

    param task_update: Поля для частичного обновления задачи.
    param task: Задача, которую нужно обновить.
    param session: Асинхронная сессия базы данных.
    return: Обновленная задача.
    raises HTTPException: При возникновении ошибки.
    """
    return await TaskCRUD.update_task(
        session=session,
        task=task,
        task_update=task_update,
        partial=True,
    )


@router.delete('/{task_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task: SchemaTask = Depends(task_by_id),
    session: AsyncSession = Depends(db_fastapi_connect.scoped_session_dependency),    
):
    """
    Удаляет задачу по ID.

    param task: Задача, которую нужно удалить.
    param session: Асинхронная сессия базы данных.
    return: None
    raises HTTPException: При возникновении ошибки.
    """
    return await TaskCRUD.delete_task(
        session=session,
        task=task,
    )


@router_list.get('/', response_model=TasksResponseSchema, status_code=status.HTTP_200_OK)
async def get_list_tasks(
    column: str | None = 'title',
    sort: str | None = 'desc',
    page: int | None = 1,
    limit: int | None = 10,
    column_search: str | None = None,
    input_search: str | None = None,
    session: AsyncSession = Depends(db_fastapi_connect.scoped_session_dependency)
):
    """
    Получает список задач.

    param column_search: Поле для поиска.
    param input_search: Значение для поиска.
    param column: Поле для сортировки.
    param sort: Направление сортировки.
    param page: Номер страницы.
    param limit: Количество задач на странице.
    param session: Асинхронная сессия базы данных.
    return: Список задач c пагинацией.
    raises HTTPException: При возникновении ошибки.
    """
    return await TaskCRUD.get_tasks(
        session=session,
        column=column,
        sort=sort,
        page=page,
        limit=limit,
        column_search=column_search,
        input_search=input_search,
    )