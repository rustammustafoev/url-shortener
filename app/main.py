from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.base import api_router
from app.db import models, database


def get_application():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    models.Base.metadata.create_all(bind=database.engine)
    app.include_router(api_router)

    return app


app = get_application()