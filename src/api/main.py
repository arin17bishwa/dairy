from fastapi import FastAPI

from .routes.chat import router as chat_router
from ..core.container import create_rag_pipeline


def create_app() -> FastAPI:
    app = FastAPI(
        title="Personal Journal Assistant",
    )


    app.state.rag_pipeline=create_rag_pipeline()


    app.include_router(chat_router)

    return app


app = create_app()