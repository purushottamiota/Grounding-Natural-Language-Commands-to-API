from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.models.nlp_model import nlp_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    nlp_pipeline.load_model()
    yield
    # Unload model on shutdown
    nlp_pipeline.unload_model()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
