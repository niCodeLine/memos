from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routes.reminders import router as reminders_router
import api.log as log
import api.setup.setup as setup

# setting logger
logger = log.ger(
    __name__,
    'DEBUG',
    file_name='api'
)

# setting API
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # executes on startup
    logger.info("Starting up.")

    # ensure databases and tables are ready
    setup.main()
    
    yield
    
    # at shutdown
    logger.info("Shutting down.")

app = FastAPI(
    title = 'Reminders API',
    description = 'API for managing reminders and memos',
    version='0.2.0',
    lifespan=lifespan
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