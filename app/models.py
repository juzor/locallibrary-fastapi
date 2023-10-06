from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum
import sqlalchemy as sa
import sqlalchemy.orm as so
from .database import Model


class Permission:
    # patron
    BORROW = 1
    RETURN = 2
    RENEW = 4
    RESERVE = 8
    PAY_FINES = 16
    # librarian (includes permissions above)
    ADD_NEW_BOOK = 32
    REMOVE_BOOK = 64
    # admin (includes permissions above)
    SUSPEND_USER = 128
    ADMIN = 256
class StatusEnum(Enum):
    ON_LOAN = 'o'
    ON_HOLD = 'h'
    AVAILABLE = 'a'
    MAINTENANCE = 'm'

BookGenre = sa.Table(
    'books_genres',
    Model.metadata,
    sa.Column('book_id', sa.ForeignKey('books.id'), primary_key=True, nullable=False),
    sa.Column('genre_id', sa.ForeignKey('genres.id'), primary_key=True, nullable=False)
)

class Language(Model):
    __tablename__ = 'languages'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, unique=True)

    books: so.WriteOnlyMapped['Book'] = so.relationship(back_populates='language')

    def __repr__(self):
        return f'Language({self.id}, "{self.name}")'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name' : self.name
        }

class Author(Model):
    __tablename__ = 'authors'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    date_of_birth: so.Mapped[Optional[datetime]]
    date_of_death: so.Mapped[Optional[datetime]]

    books: so.Mapped[list['Book']] = so.relationship(
        cascade='all, delete-orphan', back_populates='author'
    )

    def __repr__(self):
        return f'Author({self.id}, "{self.name}")'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name' : self.name
        }
    
class Book(Model):
    __tablename__ = 'books'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('authors.id'), index=True)
    summary: so.Mapped[Optional[str]] = so.mapped_column(sa.String(1000))
    isbn: so.Mapped[str] = so.mapped_column(sa.String(20), unique=True)
    img_url: so.Mapped[Optional[str]] = so.mapped_column(sa.String())
    language_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('languages.id'), index=True)

    author: so.Mapped['Author'] = so.relationship(
        back_populates='books'
    )

    book_instances: so.Mapped[list['BookInstance']] = so.relationship(
        cascade='all, delete', back_populates='book'
    )

    genres: so.Mapped[list['Genre']] = so.relationship(
        secondary=BookGenre, back_populates='books'
    )

    language: so.Mapped[Optional['Language']] = so.relationship(
        back_populates='books'
    )

    def __repr__(self):
        return f'Book({self.id}, "{self.title}")'
    
    def to_dict(self):
        return {
            'id' : self.id,
            'title' : self.title,
            'summary' : self.summary,
            'isbn' : self.isbn,
            'author': self.author.to_dict()
        }
    
class BookInstance(Model):
    __tablename__ = 'book_instances'

    id: so.Mapped[UUID] = so.mapped_column(default=uuid4, primary_key=True)
    book_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('books.id'), index=True)
    imprint: so.Mapped[str] = so.mapped_column(sa.String(200))
    due_date: so.Mapped[datetime] = so.mapped_column(nullable=True)
    status: so.Mapped[StatusEnum] = so.mapped_column(
        sa.Enum(StatusEnum), 
        default=StatusEnum.MAINTENANCE
    )

    book: so.Mapped['Book'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='book_instances'
    )

    def __repr__(self):
        return f'BookInstance({self.id.hex})'
    
    def is_overdue(self):
        """Returns True if the bookinstance is due, False otherwise."""
        return self.due_date < datetime.today()
    
    def to_dict(self):
        return {
            'id' : self.id.hex,
            'imprint' : self.imprint,
            'due_date' : self.due_date
        }
    
class Genre(Model):
    __tablename__ = 'genres'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index=True, unique=True)

    books: so.Mapped[list['Book']] = so.relationship(
        secondary=BookGenre, back_populates='genres'
    )

    def __repr__(self):
        return f'Genre({self.id}, "{self.name}")'
    
    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
        }
    
