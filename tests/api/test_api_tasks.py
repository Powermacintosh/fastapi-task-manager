import pytest
from fastapi import status

class TestTaskAPI:
    """
    Тесты для API менеджера задач.
    
    Тесты для корректного создания, получения,
    частичного обновления, полного обновления и удаления задачи.
    """
    
    @pytest.fixture
    def test_create_task(self, client):
        """
        Тест корректного создания задачи.
        """
        response_task = client.post(
            '/api/v1/task/create', 
            json={
                'title': 'Create Task', 
                'description': None,
            }
        )
        data_response_task = response_task.json()
        assert response_task.status_code == status.HTTP_201_CREATED
        assert data_response_task["title"] == 'Create Task'
        assert data_response_task["description"] == None
        assert data_response_task["status"] == 'created'
        return data_response_task
    
    @pytest.mark.asyncio
    async def test_get_task(self, client, test_create_task):
        assert test_create_task is not None
        response = client.get(f"/api/v1/task/{test_create_task['id']}")
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task["id"] == test_create_task["id"]
        assert data_response_task["title"] == test_create_task["title"]
        assert data_response_task["description"] == test_create_task["description"]
        assert data_response_task["status"] == test_create_task["status"]
    
    @pytest.mark.asyncio
    async def test_update_task(self, client, test_create_task):
        assert test_create_task is not None
        response = client.put(f"/api/v1/task/{test_create_task['id']}", json={
            'title': 'Updated Task',
            'description': 'Updated Description',
            'status': 'in_progress',
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task["id"] == test_create_task["id"]
        assert data_response_task["title"] == 'Updated Task'
        assert data_response_task["description"] == 'Updated Description'
        assert data_response_task["status"] == 'in_progress'
    
    @pytest.mark.asyncio
    async def test_update_partial_task(self, client, test_create_task):
        assert test_create_task is not None
        response = client.patch(f"/api/v1/task/{test_create_task['id']}", json={
            'title': 'Updated Partial Task',
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task["id"] == test_create_task["id"]
        assert data_response_task["title"] == 'Updated Partial Task'
        assert data_response_task["description"] == test_create_task["description"]
        assert data_response_task["status"] == test_create_task["status"]

        response = client.patch(f"/api/v1/task/{test_create_task['id']}", json={
            'description': 'Updated Partial Task',
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task["id"] == test_create_task["id"]
        assert data_response_task["title"] == 'Updated Partial Task'
        assert data_response_task["description"] == 'Updated Partial Task'
        assert data_response_task["status"] == test_create_task["status"]

        response = client.patch(f"/api/v1/task/{test_create_task['id']}", json={
            'status': 'in_progress',
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task["id"] == test_create_task["id"]
        assert data_response_task["title"] == 'Updated Partial Task'
        assert data_response_task["description"] == 'Updated Partial Task'
        assert data_response_task["status"] == 'in_progress'

        response = client.patch(f"/api/v1/task/{test_create_task['id']}", json={
            'description': 'Completed Partial Task',
            'status': 'completed',
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task["id"] == test_create_task["id"]
        assert data_response_task["title"] == 'Updated Partial Task'
        assert data_response_task["description"] == 'Completed Partial Task'
        assert data_response_task["status"] == 'completed'

    @pytest.mark.asyncio
    async def test_delete_task(self, client, test_create_task):
        assert test_create_task is not None
        response = client.delete(f"/api/v1/task/{test_create_task['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = client.get(f"/api/v1/task/{test_create_task['id']}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data_response_task = response.json()
        assert data_response_task["detail"] == f'Задача {test_create_task["id"]} не найдена!'

class TestTasksListAPI:
    """
    Тесты для списка задач.

    Тесты для корректного получения списка задач без параметров.
    Тесты для корректного получения списка задач с параметрами пагинации.
    Тесты для корректного получения списка задач с параметрами поиска.
    Тесты для корректного получения списка задач с параметрами сортировки.
    """

    @pytest.fixture
    def test_create_list_tasks(self, client):
        """
        Тест корректного создания списка задач.
        """
        created_tasks = []
        for task in range(1, 33):
            response = client.post("/api/v1/task/create",
                json={
                    'title': f'Create Task {task}',
                    'description': f'Description Task {task}',
                }
            )
            assert response.status_code == status.HTTP_201_CREATED
            created_tasks.append(response.json())
        return created_tasks
        
    @pytest.mark.asyncio
    async def test_get_list_tasks(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        response = client.get("/api/v1/tasks/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pages_count"] >= 1
        assert data["total"] >= len(data["tasks"])
        assert data["total"] >= len(test_create_list_tasks)
        assert len(data["tasks"]) <= len(test_create_list_tasks)

    @pytest.mark.asyncio
    async def test_get_list_tasks_with_pagination(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        response = client.get("/api/v1/tasks/?page=2&limit=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pages_count"] >= 2
        assert data["total"] >= len(data["tasks"])
        assert data["total"] >= len(test_create_list_tasks)
        assert len(data["tasks"]) < len(test_create_list_tasks)

    @pytest.mark.asyncio
    async def test_get_list_tasks_with_search_title(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        response = client.get("/api/v1/tasks/?column_search=title&input_search=Create Task")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pages_count"] >= 1
        assert data["total"] >= len(data["tasks"])
        for task in data["tasks"]:
            assert task["title"].startswith("Create Task")
    
    @pytest.mark.asyncio
    async def test_get_list_tasks_with_search_description(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        response = client.get("/api/v1/tasks/?column_search=description&input_search=Description Task")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pages_count"] >= 1
        assert data["total"] >= len(data["tasks"])
        for task in data["tasks"]:
            assert task["description"].startswith("Description Task")
    
    @pytest.mark.asyncio
    async def test_get_list_tasks_with_search_status_created(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        response = client.get("/api/v1/tasks/?column_search=status&input_search=created")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pages_count"] >= 1
        assert data["total"] >= len(data["tasks"])
        for task in data["tasks"]:
            assert task["status"] == "created"

    @pytest.mark.asyncio
    async def test_update_status_task_created_to_in_progress(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        for index, task in enumerate(test_create_list_tasks):
            if index < 11:
                response = client.patch(f"/api/v1/task/{task['id']}", json={"status": "in_progress"})
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["status"] == "in_progress"
        
    @pytest.mark.asyncio
    async def test_get_list_tasks_with_search_status_in_progress(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        response = client.get("/api/v1/tasks/?column_search=status&input_search=in_progress")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pages_count"] >= 1
        assert data["total"] >= len(data["tasks"])
        for task in data["tasks"]:
            assert task["status"] == "in_progress"

    @pytest.mark.asyncio
    async def test_update_status_task_in_progress_to_completed(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        for index, task in enumerate(test_create_list_tasks):
            if index >= 11 and index <= 21:
                response = client.patch(f"/api/v1/task/{task['id']}", json={"status": "completed"})
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["status"] == "completed"
     
    @pytest.mark.asyncio
    async def test_get_list_tasks_with_search_status_completed(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        response = client.get("/api/v1/tasks/?column_search=status&input_search=completed")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pages_count"] >= 1
        assert data["total"] >= len(data["tasks"])
        for task in data["tasks"]:
            assert task["status"] == "completed"

    @pytest.mark.asyncio
    async def test_get_list_tasks_with_sort_asc(self, client, test_create_list_tasks):
        assert test_create_list_tasks is not None and type(test_create_list_tasks) == list
        response = client.get("/api/v1/tasks/?sort=asc&column=description&limit=100")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pages_count"] >= 1
        assert data["total"] >= len(data["tasks"])
        assert data["tasks"] == sorted(data["tasks"], key=lambda x: x["description"])
        

class TestMockAPI:
    """
    Тесты для неправильного создания задач.
    Проверяем создание элемента с отсутствующим полем 'title'
    и получение элемента с недопустимым ID.
    """
    @pytest.mark.asyncio
    async def test_create_item_with_missing_fields(self, client):
        response = client.post(
            "/api/v1/task/create", 
            json={
                "name": "Test Item",
            }
        )
        assert response.status_code == 422
        assert "title" in response.json()["detail"][0]["loc"]

    @pytest.mark.asyncio
    async def test_get_item_with_invalid_id(self, client):
        response = client.get("/api/v1/task/invalid_id")
        assert response.status_code == 404
        data_response_task = response.json()
        assert data_response_task["detail"] == 'Задача invalid_id не найдена!'
    
    @pytest.mark.asyncio
    async def test_update_item_with_invalid_id(self, client):
        response = client.patch("/api/v1/task/invalid_id", json={"title": "Test Item"})
        assert response.status_code == 404
        data_response_task = response.json()
        assert data_response_task["detail"] == 'Задача invalid_id не найдена!'
    
    @pytest.mark.asyncio
    async def test_delete_item_with_invalid_id(self, client):
        response = client.delete("/api/v1/task/invalid_id")
        assert response.status_code == 404
        data_response_task = response.json()
        assert data_response_task["detail"] == 'Задача invalid_id не найдена!'
    
    
    