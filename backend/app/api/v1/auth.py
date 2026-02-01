from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, UserType
from app.schemas import (
    UserRegister,
    UserLogin,
    Token,
    TokenRefresh,
    UserResponse,
    UserUpdate,
)
from app.core import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user (driver or fleet operator).
    
    - Validates phone uniqueness
    - Hashes password
    - Returns user profile
    """
    # Check if phone exists
    existing = db.query(User).filter(User.phone == data.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )
    
    # Check email if provided
    if data.email:
        existing_email = db.query(User).filter(User.email == data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Create user
    user = User(
        type=data.type,
        name=data.name,
        phone=data.phone,
        email=data.email,
        password_hash=hash_password(data.password),
        license_number=data.license_number,
        experience_years=data.experience_years,
        company_name=data.company_name,
        gst_number=data.gst_number,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with phone/email and password.
    
    Returns access and refresh tokens.
    
    Demo credentials:
    - Email: admin@neurologistics.com
    - Password: admin123
    """
    # Demo mode - accept demo credentials without database
    demo_credentials = {
        "admin@neurologistics.com": {"password": "admin123", "name": "Admin User", "type": "admin"},
        "driver@neurologistics.com": {"password": "driver123", "name": "Demo Driver", "type": "driver"},
        "operator@neurologistics.com": {"password": "operator123", "name": "Fleet Operator", "type": "fleet_operator"},
        "+919999999999": {"password": "demo123", "name": "Demo User", "type": "driver"},
    }
    
    # Check for demo login (works without database)
    login_key = data.phone  # phone field is used for both phone and email
    if login_key in demo_credentials:
        demo_user = demo_credentials[login_key]
        if data.password == demo_user["password"]:
            # Create tokens with demo user ID
            import uuid
            demo_user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, login_key))
            access_token = create_access_token(subject=demo_user_id)
            refresh_token = create_refresh_token(subject=demo_user_id)
            
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
    
    # Try database login (if available)
    try:
        user = db.query(User).filter(
            (User.phone == data.phone) | (User.email == data.phone)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone/email or password",
            )
        
        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password not set. Please reset your password.",
            )
        
        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone/email or password",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )
        
        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    except Exception as e:
        if "demo" in str(e).lower() or "connection" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available. Use demo credentials: admin@neurologistics.com / admin123",
            )
        raise


@router.post("/refresh", response_model=Token)
def refresh_token(data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    payload = decode_token(data.refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new tokens
    access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user profile.
    """
    update_data = data.model_dump(exclude_unset=True)
    
    # Check email uniqueness if updating
    if "email" in update_data and update_data["email"]:
        existing = db.query(User).filter(
            User.email == update_data["email"],
            User.id != current_user.id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
