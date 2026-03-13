import os
from typing import Optional, List
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from python_keycloak import KeycloakOpenID
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Keycloak Configuration
KC_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
KC_REALM = os.getenv("KEYCLOAK_REALM", "master")
KC_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "expert-agent")
KC_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

keycloak_openid = KeycloakOpenID(
    server_url=KC_SERVER_URL,
    client_id=KC_CLIENT_ID,
    realm_name=KC_REALM,
    client_secret_key=KC_CLIENT_SECRET
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"{KC_SERVER_URL}/realms/{KC_REALM}/protocol/openid-connect/auth",
    tokenUrl=f"{KC_SERVER_URL}/realms/{KC_REALM}/protocol/openid-connect/token",
)

class UserToken(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    roles: List[str] = []

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserToken:
    """
    Validates the JWT token against Keycloak and extracts user info.
    """
    try:
        # 1. Get public key for signature verification
        key_der = keycloak_openid.public_key()
        public_key = f"-----BEGIN PUBLIC KEY-----\n{key_der}\n-----END PUBLIC KEY-----"

        # 2. Decode and validate JWT
        # Optimization: In high-traffic environments, cache the public key.
        payload = jwt.decode(
            token, 
            public_key, 
            algorithms=["RS256"], 
            audience="account" # Adjust based on Keycloak token audience
        )
        
        # 3. Extract user info
        user_id = payload.get("sub")
        username = payload.get("preferred_username")
        email = payload.get("email")
        
        # 4. Extract roles from Keycloak-specific fields
        # Usually found in realm_access.roles or resource_access.client.roles
        realm_roles = payload.get("realm_access", {}).get("roles", [])
        resource_roles = payload.get("resource_access", {}).get(KC_CLIENT_ID, {}).get("roles", [])
        all_roles = list(set(realm_roles + resource_roles))

        if user_id is None or username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return UserToken(
            id=user_id,
            username=username,
            email=email,
            roles=all_roles
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

def has_role(required_role: str):
    """
    Dependency to enforce role-based access control.
    """
    def role_checker(user: UserToken = Depends(get_current_user)):
        if required_role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_checker
