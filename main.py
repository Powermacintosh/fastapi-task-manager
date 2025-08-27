import uvicorn, pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from core.config import settings
from api_v1 import router as router_v1

app = FastAPI(
    title='API Manager Tasks',
    description='Простой менеджер задач на FastAPI с использованием асинхронного драйвера для SQLAlchemy и базы данных PostgreSQL',
    version='1.0.0',
    # docs_url=None,
    # redoc_url=None,
)

app.mount('/static', StaticFiles(directory='static'), name='static')

@app.get('/docs/', include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + ' - Custom Swagger UI',
        swagger_css_url='/static/swagger-custom-ui.css',
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.methods,
    allow_headers=settings.cors.headers,
)

app.include_router(router=router_v1, prefix=settings.api_v1_prefix)


if __name__ == '__main__':
    cwd = pathlib.Path(__file__).parent.resolve()
    # uvicorn.run('main:app', host='0.0.0.0', port=settings.api_v1_port, reload=True)
    uvicorn.run('main:app', host='0.0.0.0', port=settings.api_v1_port, reload=False, log_config=f'{cwd}/configs/log_config.ini')
