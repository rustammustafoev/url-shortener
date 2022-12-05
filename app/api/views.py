from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import validators

from app.db import schemas, database, crud
from app.core import tools

router = APIRouter()


@router.get("/")
def read_root():
    return "Welcome to the URL Shortener API"


@router.post("/url", response_model=schemas.URLInfo)
def create_url(url: schemas.URLBase, db: Session = Depends(database.get_db)):
    if not validators.url(url.target_url):
        tools.raise_bad_request(message="Your provided URL is not valid")

    db_url = crud.create_db_url(db=db, url=url)
    return crud.get_admin_info(db_url)


@router.get("/{url_key}")
def forward_to_target_url(
        url_key: str,
        request: Request,
        db: Session = Depends(database.get_db)
    ):
    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        return RedirectResponse(db_url.target_url)
    else:
        tools.raise_not_found(request)


@router.get(
    "/admin/{secret_key}",
    name="administration info",
    response_model=schemas.URLInfo,
)
def get_url_info(
    secret_key: str, request: Request, db: Session = Depends(database.get_db)
):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
        crud.update_db_clicks(db=db, db_url=db_url)
        return crud.get_admin_info(db_url)
    else:
        tools.raise_not_found(request)


@router.delete("/admin/{secret_key}")
def delete_url(
    secret_key: str, request: Request, db: Session = Depends(database.get_db)
):
    if db_url := crud.deactivate_db_url_by_secret_key(db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        tools.raise_not_found(request)
