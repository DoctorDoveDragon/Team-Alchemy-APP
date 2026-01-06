from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta

from app.database import get_session
from app.models import User, Document
from app.schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    DocumentCreate, DocumentResponse
)
from app.auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

# Auth routes
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """Register a new user"""
    # Check if user already exists
    statement = select(User).where(
        (User.email == user_data.email) | (User.username == user_data.username)
    )
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


@auth_router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, session: Session = Depends(get_session)):
    """Login and get access token"""
    statement = select(User).where(User.username == user_credentials.username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# Document routes
doc_router = APIRouter(prefix="/documents", tags=["Documents"])


@doc_router.post("/", response_model=DocumentResponse)
def create_document(
    document_data: DocumentCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """Create a new document"""
    # Get user from database
    statement = select(User).where(User.username == current_user.username)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create document
    document = Document(
        title=document_data.title,
        content=document_data.content,
        citation_style=document_data.citation_style,
        author_id=user.id
    )
    
    session.add(document)
    session.commit()
    session.refresh(document)
    
    return document


# Include routers
router.include_router(auth_router)
router.include_router(doc_router)
