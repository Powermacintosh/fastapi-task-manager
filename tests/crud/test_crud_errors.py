# tests/test_crud_errors.py
import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from uuid import uuid4
from api_v1.tasks.crud import TaskCRUD
from api_v1.tasks.schemas import (
    TaskBase,
    TaskCreate,
    SchemaTask,
    TaskUpdate,
    TaskUpdatePartial,
)
from pydantic import ValidationError

class TestTaskCRUDErrors:
    """
    Тесты для проверки корректной работы CRUD операций.
    """
    @pytest.mark.asyncio
    async def test_create_task_integrity_error(self):
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock(
            side_effect=IntegrityError("Integrity Error", {}, None)
        )
        
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            status="created"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await TaskCRUD.create_task(mock_session, task_data)
            
        assert exc_info.value.status_code == 409
        assert "конфликтная ситуация" in str(exc_info.value.detail)


    @pytest.mark.asyncio
    async def test_create_task_general_error(self):
        mock_session = AsyncMock()
        mock_session.add = MagicMock(side_effect=Exception("Unexpected error"))
        
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            status="created"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await TaskCRUD.create_task(mock_session, task_data)
        
        assert exc_info.value.status_code == 500
        assert "ошибка при создании задачи" in str(exc_info.value.detail)


    @pytest.mark.asyncio
    async def test_update_task_sqlalchemy_error(self):
        mock_session = AsyncMock()
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")
        
        task_id = str(uuid4())
        task = SchemaTask(id=task_id, title="Test", description="Test", status="created")
        update_data = TaskUpdate(title="Updated", status="in_progress")
        
        with pytest.raises(HTTPException) as exc_info:
            await TaskCRUD.update_task(mock_session, task, update_data)
            
        assert exc_info.value.status_code == 500
        assert "ошибка при обновлении" in str(exc_info.value.detail)


    @pytest.mark.asyncio
    async def test_update_task_general_error(self):
        mock_session = AsyncMock()
        mock_session.commit.side_effect = Exception("Unexpected error")
        task_id = str(uuid4())
        task = SchemaTask(id=task_id, title="Test", description="Test", status="created")
        update_data = TaskUpdatePartial(title="Updated")
        
        with pytest.raises(HTTPException) as exc_info:
            await TaskCRUD.update_task(mock_session, task, update_data, partial=True)
            
        assert exc_info.value.status_code == 500
        assert "ошибка при обновлении" in str(exc_info.value.detail)


    @pytest.mark.asyncio
    async def test_delete_task_integrity_error(self):
        mock_session = AsyncMock()
        mock_session.commit.side_effect = IntegrityError("Integrity Error", {}, None)
        
        task_id = str(uuid4())
        task = SchemaTask(id=task_id, title="Test", description="Test", status="created")
        
        with pytest.raises(HTTPException) as exc_info:
            await TaskCRUD.delete_task(mock_session, task)
            
        assert exc_info.value.status_code == 409
        assert "конфликтная ситуация" in str(exc_info.value.detail)
    

    @pytest.mark.asyncio
    async def test_delete_task_general_error(self):
        mock_session = AsyncMock()
        mock_session.commit.side_effect = Exception("Unexpected error")
        
        task_id = str(uuid4())
        task = SchemaTask(id=task_id, title="Test", description="Test", status="created")
        
        with pytest.raises(HTTPException) as exc_info:
            await TaskCRUD.delete_task(mock_session, task)
            
        assert exc_info.value.status_code == 500
        assert "ошибка при удалении" in str(exc_info.value.detail)


    @pytest.mark.asyncio
    async def test_get_tasks_unknown_status(self):
        mock_session = AsyncMock()
        
        with pytest.raises(ValueError) as exc_info:
            await TaskCRUD.get_tasks(
                session=mock_session,
                column_search='status',
                input_search='INVALID_STATUS'
            )
        
        assert "Неизвестный статус задачи" in str(exc_info.value)
    

    @pytest.mark.asyncio
    async def test_get_tasks_pagination_and_sorting(self):
        # Создаем мок сессии
        mock_session = AsyncMock()
        
        # Настраиваем мок для вызовов execute
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 25  # Всего 25 задач
        
        mock_data_result = MagicMock()
        mock_data_result.scalars.return_value.all.return_value = []
        
        # Устанавливаем side_effect для последовательных вызовов
        mock_session.execute.side_effect = [mock_count_result, mock_data_result]
        
        # Вызываем метод с пагинацией и сортировкой
        result = await TaskCRUD.get_tasks(
            session=mock_session,
            page=2,  # Вторая страница
            limit=10,  # 10 элементов на странице
            column="title",  # Сортировка по заголовку
            sort="asc"  # По возрастанию
        )
        
        # Проверяем результаты
        assert result.total == 25
        assert result.pages_count == 3  # 25 / 10 с округлением вверх
        assert len(result.tasks) == 0  # Мок возвращает пустой список
        
        # Проверяем, что было 2 вызова execute
        assert mock_session.execute.call_count == 2
        
        # Проверяем второй вызов (первый - это подсчет)
        args, kwargs = mock_session.execute.call_args_list[1]
        stmt = str(args[0])
        
        # Проверяем наличие ключевых элементов SQL-запроса
        assert "ORDER BY tasks.title ASC" in stmt
        assert "LIMIT :param_1" in stmt
        assert "OFFSET :param_2" in stmt


    @pytest.mark.asyncio
    async def test_update_task_validation_error(self):
        mock_session = AsyncMock()
        
        # Настраиваем мок для вызова commit, чтобы выбросить IntegrityError
        mock_session.commit.side_effect = IntegrityError("Test error", None, None)
        
        # Создаем валидные данные
        task = SchemaTask(
            id=str(uuid4()),
            title="Test Task",
            description="Test Description",
            status="created"
        )
        
        valid_update = TaskUpdate(
            title="Valid Title",
            description="Updated Description",
            status="in_progress"
        )
        
        # Проверяем обработку IntegrityError
        with pytest.raises(HTTPException) as exc_info:
            await TaskCRUD.update_task(
                session=mock_session,
                task=task,
                task_update=valid_update,
                partial=False
            )
        
        assert exc_info.value.status_code == 409
        assert "конфликтная ситуация" in str(exc_info.value.detail)
    

    # @pytest.mark.asyncio
    async def test_task_title_validation(self):
        # Проверка минимальной длины
        with pytest.raises(ValidationError) as exc_info:
            TaskBase(title="", description="Test")
        assert "String should have at least 1 character" in str(exc_info.value)
        
        # Проверка максимальной длины
        with pytest.raises(ValidationError) as exc_info:
            TaskBase(title="A" * 101, description="Test")
        assert "String should have at most 100 characters" in str(exc_info.value)
        
        # Проверка валидного значения
        task = TaskBase(title="Valid Title", description="Test")
        assert task.title == "Valid Title"
    