from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from api.auth import (
    authenticate_user, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    User
)
from data.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

@router.post("/login", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Save failed attempt to AuditLog
        from api.models import AuditLog
        import uuid
        db.add(AuditLog(
            id=uuid.uuid4().hex,
            action="LOGIN_FAILED",
            target=form_data.username,
            meta_info={"ip": request.client.host, "user_agent": request.headers.get("user-agent", "Unknown")}
        ))
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Save UserSession and AuditLog
    from api.models import UserSession, AuditLog
    import uuid
    from datetime import datetime
    
    session_id = uuid.uuid4().hex
    
    db.add(UserSession(
        id=session_id,
        user_id=user.id,
        domain_id=user.domain_id if hasattr(user, 'domain_id') else None,
        tenant_id=user.tenant_id if hasattr(user, 'tenant_id') else None,
        device_info=request.headers.get("user-agent", "Unknown"),
        ip_address=request.client.host,
        login_at=datetime.utcnow(),
        last_activity=datetime.utcnow()
    ))
    
    db.add(AuditLog(
        id=uuid.uuid4().hex,
        user_id=user.id,
        domain_id=user.domain_id if hasattr(user, 'domain_id') else None,
        tenant_id=user.tenant_id if hasattr(user, 'tenant_id') else None,
        action="USER_LOGIN_SUCCESS",
        target=user.username,
        meta_info={"ip": request.client.host, "session_id": session_id}
    ))
    db.commit()
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

@router.post("/logout")
async def logout(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from api.models import AuditLog
    import uuid
    db.add(AuditLog(
        id=uuid.uuid4().hex,
        user_id=current_user.id,
        domain_id=current_user.domain_id if hasattr(current_user, 'domain_id') else None,
        tenant_id=current_user.tenant_id if hasattr(current_user, 'tenant_id') else None,
        action="USER_LOGOUT",
        target=current_user.username,
        meta_info={"ip": request.client.host}
    ))
    db.commit()
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
