from typing import List
import sqlalchemy as sa
import sqlalchemy.orm as so
from .. import models, database, schemas, utils, oauth2
from fastapi import APIRouter, Response, status, HTTPException, Depends

router = APIRouter(
    tags=["Catalogue"]
)

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
            detail="Access denied"
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
    db.add(new_book)
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
            detail="Access denied"
        )
    book = db.get(models.Book, id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book with id: {id} found"
        )
    book.update(updated_book)
    db.commit()
    return book

@router.delete('/books/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_book(id: int, current_user: models.User = Depends(oauth2.get_current_user), db: so.Session=Depends(database.get_db)):
    if not current_user.is_librarian() and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied"
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
            detail="Access denied"
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
            detail="Access denied"
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