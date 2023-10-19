from typing import List
from uuid import UUID
from pydantic import UUID4
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timedelta
from .. import models, database, schemas, utils, oauth2
from fastapi import APIRouter, Response, status, HTTPException, Depends

router = APIRouter(
    tags=["Catalogue"]
)

# Book CRUD operations
@router.get('/books', response_model=List[schemas.BookOut])
def get_books(db: so.Session=Depends(database.get_db)):
    books = db.execute(sa.select(models.Book)).all()
    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No books in the database"
        )
    return [{**book[0].to_dict()} for book in books]

@router.get('/books/{id}', response_model=schemas.BookDetailOut)
def get_book(id: int, db: so.Session=Depends(database.get_db)):
    book = db.get(models.Book, id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book with id: {id} found"
        )
    return book.to_dict()

@router.post('/books', status_code=status.HTTP_201_CREATED, response_model=schemas.BookOut)
def create_book(
    book: schemas.BookCreate, 
    current_user: models.User = Depends(oauth2.get_current_user), 
    db: so.Session=Depends(database.get_db)
    ):
    if not current_user.is_librarian() :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    author = db.get(models.Author, book.author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book author with id: {book.author_id} not found. Add author first"
        )
    new_book = models.Book(
        title = book.title,
        summary = book.summary,
        isbn = book.isbn,
        img_url = book.img_url,
        author_id = book.author_id,
    )
    if book.language_id:
        language = db.get(models.Language, book.language_id)
        if not language:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Language with id: {book.language_id} not found. Add author first"
            )
        new_book.language_id = book.language_id
    if book.copies and book.imprint:
        for i in range(book.copies):
            bk = models.BookInstance(
                imprint = book.imprint
            )
            new_book.book_instances.append(bk)
    for genre in book.genres:
        g = db.scalar(sa.select(models.Genre).where( models.Genre.name.ilike(f"%{genre}%")))
        if not g:
            g = models.Genre(
                name = genre
            )
            db.add(g)
        g.books.append(new_book)
    #db.add(new_book)
    db.commit()
    return new_book.to_dict()

@router.put('/books/{id}', response_model=schemas.BookOut)
def update_book(
    id: int, 
    updated_book: schemas.BookUpdate,
    current_user: models.User = Depends(oauth2.get_current_user), 
    db: so.Session=Depends(database.get_db)
    ):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    book = db.get(models.Book, id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book with id: {id} found"
        )
    book.update(updated_book)
    print(book.to_dict())
    db.commit()
    return book.to_dict()

@router.delete('/books/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int, current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    book = db.get(models.Book, id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book with id: {id} found"
        )
    db.delete(book)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Book loan operations
@router.get('/all-loans', response_model=List[schemas.BookInstanceOut])
def all_loans(current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied"
        )
    all_borrowed = db.scalars(
        sa.select(models.BookInstance).where(models.BookInstance.status == models.StatusEnum.ON_LOAN)
    ).all()
    if not all_borrowed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No borrowed books"
        )
    # [{**author[0].to_dict()} for author in authors]
    return [{**borrowed.to_dict()} for borrowed in all_borrowed]

@router.post('/renew-loan/{uuid}', response_model=schemas.BookInstanceOut)
def renew_loan(uuid: UUID4, current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    book_instance = db.get(models.BookInstance, uuid)
    if not book_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book instance with id: {uuid}"
        )
    book_instance.due_date = datetime.now() + timedelta(days=30)
    db.commit()
    db.refresh(book_instance)
    return book_instance

@router.post('/return-loan/{uuid}', response_model=schemas.BookInstanceOut)
def return_loan(uuid: UUID4, current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    book_instance = db.get(models.BookInstance, uuid)
    if not book_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book instance with id: {uuid}"
        )
    book_instance.due_date = None
    book_instance.status = models.StatusEnum.AVAILABLE
    db.commit()
    return book_instance

@router.get('/my-loans', response_model=List[schemas.BookInstanceOut])
def my_loans(current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    loans = db.scalars(
        sa.select(models.BookInstance).join(
            models.BookInstance.user
        ).where(
            models.User.id == current_user.id,
            models.BookInstance.status == models.StatusEnum.ON_LOAN
        )
    )
    if not loans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currently, you have no book loans!"
        )
    return [{**loan.to_dict()} for loan in loans]

# Author CRUD operations
@router.get('/authors', response_model=List[schemas.AuthorOut])
def get_authors(db: so.Session=Depends(database.get_db)):
    authors = db.execute(sa.select(models.Author)).all()
    if not authors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No authors in the database"
        )
    return [{**author[0].to_dict()} for author in authors]

@router.get('/authors/{id}', response_model=schemas.AuthorDetailOut)
def get_author(id: int, db: so.Session=Depends(database.get_db)):
    author = db.get(models.Author, id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No author with id: {id} found"
        )
    return author.to_dict()

@router.post('/authors', status_code=status.HTTP_201_CREATED, response_model=schemas.AuthorOut)
def create_author(
    new_author: schemas.AuthorCreate, 
    current_user: models.User = Depends(oauth2.get_current_user), 
    db: so.Session=Depends(database.get_db)
    ):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    db_author = db.scalar(sa.select(models.Author).where(models.Author.name == new_author.name))
    if db_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Author already exists"
        )
    author = models.Author(**new_author.model_dump())
    db.add(author)
    db.commit()
    db.refresh(author)
    return author

@router.put('/authors/{id}', response_model=schemas.AuthorOut)
def update_author(
    id: int, 
    updated_author: schemas.AuthorCreate,
    current_user: models.User = Depends(oauth2.get_current_user), 
    db: so.Session=Depends(database.get_db)
    ):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    author = db.get(models.Author, id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No author with id: {id} found"
        )
    author.update(updated_author)
    db.commit()
    return author
    
@router.delete('/authors/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_author(
    id: int, 
    current_user: models.User = Depends(oauth2.get_current_user), 
    db: so.Session=Depends(database.get_db)
    ):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied"
        )
    author = db.get(models.Author, id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No author with id: {id} found"
        )
    db.delete(author)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Genre CRUD operations
@router.get('/genres', response_model=List[schemas.GenreOut])
def get_genres(db: so.Session=Depends(database.get_db)):
    genres = db.scalars(sa.select(models.Genre).order_by(models.Genre)).all()
    if not genres:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No genre(s) in the database"
        )
    return [{**genre.to_dict()} for genre in genres]

@router.get('/genres/{id}', response_model=schemas.GenreDetailOut)
def get_genre(id: int, db: so.Session=Depends(database.get_db)):
    genre = db.get(models.Genre, id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No genre with id: {id}"
        )
    return genre.to_dict()

@router.post('/genres', status_code=status.HTTP_201_CREATED, response_model=schemas.GenreOut)
def create_genre(
        new_genre: schemas.GenreCreate,
        current_user: models.User = Depends(oauth2.get_current_user), 
        db: so.Session=Depends(database.get_db)
    ):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    db_genre = db.scalar(sa.select(models.Genre).where(models.Genre.name == new_genre.name))
    if db_genre:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Genre already exists"
        )
    genre = models.Genre(**new_genre.model_dump())
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre.to_dict()

@router.put('/genres/{id}', response_model=schemas.GenreOut)
def update_genre(
    id: int, 
    updated_genre: schemas.GenreCreate,
    current_user: models.User = Depends(oauth2.get_current_user), 
    db: so.Session=Depends(database.get_db)
    ):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    genre = db.get(models.Genre, id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No genre with id: {id}"
        )
    genre.update(updated_genre)
    db.commit() 
    return genre

@router.delete('/genres/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(
    id: int,
    current_user: models.User = Depends(oauth2.get_current_user), 
    db: so.Session=Depends(database.get_db)
    ):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised action"
        )
    genre = db.get(models.Genre, id)
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No genre with id: {id}"
        )
    db.delete(genre)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)