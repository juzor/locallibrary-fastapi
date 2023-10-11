from typing import List
import sqlalchemy as sa
import sqlalchemy.orm as so
from .. import models, database, schemas, utils, oauth2
from fastapi import APIRouter, status, HTTPException, Depends

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: so.Session=Depends(database.get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords not the same"
        )
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    patron = db.scalar(sa.select(models.Role).where(models.Role.name == "Patron"))
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password,
        role=patron
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.to_dict()

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    user = db.get(models.User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
    if current_user.id != user.id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied"
        )
    return user.to_dict()

@router.get('/', response_model=List[schemas.UserOut])
def get_users(current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    print(current_user.role.name)
    if not current_user.is_admin() and not current_user.is_librarian():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied"
        )
    users = db.execute(sa.select(models.User)).all()
    
    return [{**user[0].to_dict()} for user in users]

@router.put('/{id}', response_model=schemas.UserOut)
def toggle_user(id: int, current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    if current_user.role.name != "Admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied"
        )
    
    user = db.get(models.User, id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
    else:
        if user.active:
            user.active = False
        else:
            user.active = True
        db.commit()
        db.refresh(user)        
    return user
    