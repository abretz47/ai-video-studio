from datetime import timedelta

from app.core.config import settings
from app.core.database import get_db
from app.core.middleware import get_current_active_user, record_user_login
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.user_management_service import UserManagementService
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()


def _not_deleted(query, model):
    return query.filter(model.is_deleted.is_(False))


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """User registration.

    - The first user (when no users exist) is automatically promoted to an active superuser for self-service approval and operations.
    - Subsequent users follow the existing process: inactive, unapproved, and email-unverified.
    """
    is_first_user = db.query(User).count() == 0
    # Check whether the username already exists
    if (
        _not_deleted(db.query(User), User)
        .filter(User.username == user_data.username)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # Check whether the email already exists
    if _not_deleted(db.query(User), User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    # Create a new user - inactive by default
    hashed_password = get_password_hash(user_data.password)

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        language=user_data.language,
        timezone=user_data.timezone,
        # The first user self-promotes to administrator; all others remain in the approval workflow
        is_active=is_first_user,
        is_approved=is_first_user,
        email_verified=is_first_user,
        is_admin=is_first_user,
        is_superuser=is_first_user,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    if not is_first_user:
        # Subsequent users still require email verification/approval
        service = UserManagementService(db)
        service.generate_activation_token(db_user.id)

    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """User login"""
    user = (
        _not_deleted(db.query(User), User)
        .filter(User.username == form_data.username)
        .first()
    )

    # Validate username and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        # If the user exists, increment failed login attempts
        if user:
            record_user_login(user, db, success=False)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account lock status
    if user.is_account_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="The account is locked. Please try again later or contact an administrator.",
        )

    # Check user status - only basic status is checked here; detailed checks are performed in middleware
    if not user.can_login:
        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before logging in"
            )
        elif not user.is_approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The account is pending administrator approval. Please wait patiently.",
            )
        elif not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The account has been deactivated. Please contact an administrator.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The account status is abnormal. Please contact an administrator.",
            )

    # Record successful login
    record_user_login(user, db, success=True)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information - requires an active approved user"""
    return current_user


@router.post("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email"""
    service = UserManagementService(db)
    user = service.verify_activation_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token or token has expired"
        )

    return {"message": "Email verified successfully", "user_id": user.id}


@router.post("/resend-verification/{user_id}")
def resend_verification_email(user_id: int, db: Session = Depends(get_db)):
    """Resend verification email"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email has already been verified"
        )

    service = UserManagementService(db)
    activation_token = service.generate_activation_token(user_id)

    return {"message": "Verification email resent", "activation_token": activation_token}
