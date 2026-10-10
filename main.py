import uvicorn

from src.core.settings import settings

if __name__ == '__main__':
    uvicorn.run(
        'src.app:app',
        host=settings.app.host,
        port=settings.app.port,
        log_config=None,
        access_log=False,
    )
