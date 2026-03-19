from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        # User not logged in
        return None
    
    # Normally "Bearer <token>" but via cookie it might just be the token
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
        
    payload = decode_access_token(token)
    if not payload:
        return None
        
    user_id = payload.get("sub")
    if not user_id:
        return None
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user

def get_superadmin(user: User = Depends(get_current_user_from_cookie)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    if user.role != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return user

def get_shop_admin(request: Request, user: User = Depends(get_current_user_from_cookie)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    if user.role not in ["superadmin", "shop_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
        
    # Validation against specific shop_id logic is usually tied to route params,
    # so we return user and let the route validate `user.shop_id == shop_id` or user is superadmin.
    return user
