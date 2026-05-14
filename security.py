import secrets
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "admin")


def docs_auth(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username, DOCS_USER)
    ok_pass = secrets.compare_digest(credentials.password, DOCS_PASSWORD)
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
