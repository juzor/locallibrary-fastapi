from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from .database import Model


class Author(Model):
    __tablename__ = 'authors'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

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

    author: so.Mapped['Author'] = so.relationship(
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