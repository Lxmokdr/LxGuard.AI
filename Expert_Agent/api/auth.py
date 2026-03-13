
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from data.database import get_db
import api.models as models
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "hc-hybrid-expert-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

class UserRole(str, Enum):
    ADMIN = "admin"       # Can configure system, see all docs
    DEVELOPER = "developer" # System development access
    EMPLOYEE = "employee" # Standard access to business docs
    GUEST = "guest"       # Limited access, public docs only

from pydantic import BaseModel

class User(BaseModel):
    id: str
    username: str
    role: UserRole
    tenant_id: Optional[str] = None
    domain_id: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if not hashed_password or not hashed_password.startswith('$2'):
            print(f"ERROR: Invalid hash format: {hashed_password[:10]}...")
            return False
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"ERROR: Bcrypt checkpw failed: {e}")
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def authenticate_user(db: Session, username: str, password: str):
    print(f"DEBUG: Authenticating user: {username}")
    try:
        db_user = db.query(models.User).filter(models.User.username == username).first()
        if not db_user:
            print(f"DEBUG: User not found: {username}")
            return False
        if not db_user.password_hash:
            print(f"DEBUG: User has no password hash: {username}")
            return False
        
        print(f"DEBUG: Verifying password for: {username}")
        is_valid = verify_password(password, db_user.password_hash)
        print(f"DEBUG: Password verification result: {is_valid}")
        if not is_valid:
            return False
        return db_user
    except Exception as e:
        print(f"ERROR: Exception in authenticate_user: {e}")
        import traceback
        traceback.print_exc()
        raise e

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
# Mock database of users for MVP
# In production, this would come from a DB or LDAP
MOCK_USERS = {
    "sk_admin_123": User(id="1", username="System Admin", role=UserRole.ADMIN),
    "dev-key-12345": User(id="1", username="System Admin", role=UserRole.ADMIN), # Frontend default
    "sk_employee_456": User(id="2", username="John Doe", role=UserRole.EMPLOYEE),
    "sk_guest_789": User(id="3", username="External User", role=UserRole.GUEST)
}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current user from JWT token.
    Now fetches from the database.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
        
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return User(
        id=db_user.id, 
        username=db_user.username, 
        role=UserRole(db_user.role),
        tenant_id=db_user.tenant_id,
        domain_id=db_user.domain_id
    )

async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Optional authentication - defaults to GUEST user if no token provided.
    """
    if not token:
        return User(id="guest", username="Guest User", role=UserRole.GUEST)
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return User(id="guest", username="Guest User", role=UserRole.GUEST)
            
        db_user = db.query(models.User).filter(models.User.username == username).first()
        if not db_user:
            return User(id="guest", username="Guest User", role=UserRole.GUEST)
            
        return User(
            id=db_user.id, 
            username=db_user.username, 
            role=UserRole(db_user.role),
            tenant_id=db_user.tenant_id,
            domain_id=db_user.domain_id
        )
    except JWTError:
        return User(id="guest", username="Guest User", role=UserRole.GUEST)

class AuthManager:
    """
    Manages authentication and role validation.
    """
    @staticmethod
    def check_access(user: User, allowed_roles: List[str]) -> bool:
        """
        Check if user has one of the allowed roles.
        If allowed_roles is empty, access is open to all authenticated users.
        """
        if not allowed_roles:
            return True
            
        return user.role.value in allowed_roles
