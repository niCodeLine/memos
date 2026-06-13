from fastapi import FastAPI
from .routes.reminders import router as reminders_router
import api.log as log

# setting logger
logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)

# setting API
app = FastAPI(
    title = 'Reminders API',
    description = 'API for managing reminders and memos',
    version='0.1.0'
)

@app.get("/")
async def root():
    logger.info("root endpoint accessed")

    return {
        "message": "API running.", # agregar un tipo de documentacion
        "docs": "Find documentationn at /docs"
    }
logger.debug('api set and runnning')

app.include_router(reminders_router)
logger.info('API re-running')