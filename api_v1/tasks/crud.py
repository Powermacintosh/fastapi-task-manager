from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from core.models import Task
from core.models.task import TaskStatus

from .schemas import (
    TaskCreate,
    SchemaTask,
    TaskUpdate,
    TaskUpdatePartial,
    TasksResponseSchema,
)
import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('crud_logger')

class TaskCRUD:
    
    @classmethod
    async def get_task(
        cls,
        session: AsyncSession,
        task_id: int,
    ) -> Task | None:
        return await session.get(Task, task_id)
    
    @classmethod
    async def get_tasks(
        cls,
        session: AsyncSession,
        column: str = 'title',
        sort: str = 'desc',
        page: int = 1,
        limit: int = 10,
        column_search: str | None = None,
        input_search: str | None = None,
    ) -> TasksResponseSchema:
        stmt = select(Task)
        total_stmt = select(func.count(Task.id))

        if column_search and input_search:
            if column_search in ('title', 'description'):
                input_column = getattr(Task, column_search)
                stmt = stmt.where(input_column.like(input_search + '%'))
                total_stmt = total_stmt.where(input_column.like(input_search + '%'))

            elif column_search == 'status':
                if input_search.upper() == 'CREATED':
                    stmt = stmt.where(Task.status == TaskStatus.CREATED)
                elif input_search.upper() == 'IN_PROGRESS':
                    stmt = stmt.where(Task.status == TaskStatus.IN_PROGRESS)
                elif input_search.upper() == 'COMPLETED':
                    stmt = stmt.where(Task.status == TaskStatus.COMPLETED)
                else:
                    logger.exception('Неизвестный статус задачи: %s', input_search)
                    raise ValueError(f'Неизвестный статус задачи: {input_search}')

        total_result = await session.execute(total_stmt)
        total_tasks = total_result.scalar() or 0

        # Вычисляем количество страниц
        pages_count = (total_tasks + limit - 1) // limit  # Округление вверх
        # Добавляем пагинацию к запросу
        offset = (page - 1) * limit

        task_column = getattr(Task, column)
        # определяем направление сортировки
        ordering = task_column.desc() if sort.lower() == 'desc' else task_column.asc()
        # строим запрос с сортировкой, лимитом и offset
        stmt = stmt.order_by(ordering).limit(limit).offset(offset)

        result = await session.execute(stmt)
        tasks = result.scalars().all()
        if tasks is None:
            tasks = []
        return TasksResponseSchema(
            pages_count=pages_count,
            total=total_tasks,
            tasks=tasks,
        )

    @classmethod
    async def create_task(
        cls,
        session: AsyncSession,
        task: TaskCreate,
    ) -> TaskCreate | None:
        try:
            task = Task(**task.model_dump())
            session.add(task)
            await session.commit()
            return task
        except IntegrityError:
            await session.rollback()
            logger.exception('При создании задачи: %s, возникла конфликтная ситуация', task.title)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Возникла конфликтная ситуация при создании задачи'
            )
        except Exception as e:
            await session.rollback()
            logger.exception('При создании задачи: %s, возникла ошибка: %s', task.title, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Возникла ошибка при создании задачи'
            )

    @classmethod
    async def update_task(
        cls,
        session: AsyncSession,
        task: Task,
        task_update: TaskUpdate | TaskUpdatePartial,
        partial: bool = False,
    ) -> Task | None:
        try:
            for name, value in task_update.model_dump(exclude_unset=partial).items():
                if name == 'status' and isinstance(value, str):
                    value = TaskStatus(task_update.status)
                setattr(task, name, value)
            await session.commit()
            await session.refresh(task)
            return task
        except IntegrityError:
            await session.rollback()
            logger.exception('При обновлении задачи: %s, возникла конфликтная ситуация', task.id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Возникла конфликтная ситуация при обновлении задачи'
            )
        except Exception as e:
            await session.rollback()
            logger.exception('При обновлении задачи: %s, возникла ошибка: %s', task.id, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Возникла ошибка при обновлении задачи'
            )

    @classmethod
    async def delete_task(
        cls,
        session: AsyncSession,
        task: SchemaTask,
    ) -> None:
        try:
            await session.delete(task)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            logger.exception('При удалении задачи: %s, возникла конфликтная ситуация', task.id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Возникла конфликтная ситуация при удалении задачи'
            )
        except Exception as e:
            await session.rollback()
            logger.exception('При удалении задачи: %s, возникла ошибка: %s', task.id, e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Возникла ошибка при удалении задачи'
            )