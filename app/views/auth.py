"""
Authentication routes for login and token management.
"""
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import get_settings
from app.controllers.user_controller import user_controller
from app.middlewares.auth_middleware import create_access_token
from app.schemas.token import Token

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Authenticate user
    user = user_controller.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    
    # Check if authentication failed
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user_controller.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Create access token
    access_token_expires = timedelta(
        minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    # Define token data
    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "scopes": ["user"],
    }
    
    # Add admin scope if user is superuser
    if user_controller.is_superuser(user):
        token_data["scopes"].append("admin")
    
    # Create and return token
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
