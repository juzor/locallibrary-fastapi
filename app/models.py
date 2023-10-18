from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4
from enum import Enum
import sqlalchemy as sa
import sqlalchemy.orm as so
from .database import Model, Session, get_db

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

class Updateable:
    def update(self, data):
        for attr, value in data:
            setattr(self, attr, value)

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

class Author(Updateable, Model):
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
            'name' : self.name,
            'date_of_birth': self.date_of_birth,
            'date_of_death': self.date_of_death,
            'books':[book.to_dict() for book in self.books]
        }
    
class Book(Updateable, Model):
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
        cascade='all, delete-orphan', back_populates='book'
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
            'img_url': self.img_url,
            'author': self.author.name,
            #'language': self.language.name,
            'book_instances': [book_instance.to_dict() for book_instance in self.book_instances]
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
    user_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('users.id'), index=True)

    book: so.Mapped['Book'] = so.relationship(
        lazy='joined', innerjoin=True, back_populates='book_instances'
    )

    user: so.Mapped[Optional['User']] = so.relationship(
        back_populates='book_instances'
    )

    def __repr__(self):
        return f'BookInstance({self.id.hex})'
    
    def is_overdue(self):
        """Returns True if the bookinstance is due, False otherwise."""
        return self.due_date < datetime.today()
    
    def to_dict(self):
        return {
            'id' : self.id,
            'book_id': self.book_id,
            'imprint' : self.imprint,
            'due_date' : self.due_date,
            'status' : self.status,
            'user_id': self.user_id
        }
    
class Genre(Updateable, Model):
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
            'books': [book.to_dict() for book in self.books]
        }
    
class User(Model):
    __tablename__ = 'users'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password: so.Mapped[str] = so.mapped_column(sa.String)
    active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)

    role_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('roles.id'))
    role: so.Mapped[Optional['Role']] = so.relationship(back_populates='users')
    book_instances: so.Mapped[Optional[list['BookInstance']]] = so.relationship(back_populates='user')

    def __repr__(self):
        return f'User({self.id}, "{self.name}")'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'active': self.active,
            'role': self.role.name
        }
    
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    
    def is_admin(self):
        return self.can(Permission.ADMIN)
    
    def is_librarian(self):
        return self.can(Permission.REMOVE_BOOK)
        
class Role(Model):
    __tablename__ = 'roles'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    default: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, index=True)
    permissions: so.Mapped[int] = so.mapped_column(sa.Integer)

    users: so.Mapped[list['User']] = so.relationship(back_populates='role')

    def __repr__(self):
        return f'Role({self.id}, "{self.name}")'
    
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles(session):
        roles = {
            'Patron': [Permission.BORROW, Permission.RENEW, Permission.RETURN, 
                        Permission.PAY_FINES, Permission.RESERVE],
            'Librarian': [Permission.BORROW, Permission.RENEW, Permission.RETURN, 
                            Permission.PAY_FINES, Permission.RESERVE, Permission.ADD_NEW_BOOK, 
                            Permission.REMOVE_BOOK],
            'Admin': [Permission.BORROW, Permission.RENEW, Permission.RETURN, 
                            Permission.PAY_FINES, Permission.RESERVE, Permission.ADD_NEW_BOOK, 
                            Permission.REMOVE_BOOK, Permission.SUSPEND_USER, Permission.ADMIN]
        }
        default_role = 'Patron'
        for r in roles:
            role = session.scalar(sa.select(Role).where(Role.name == r))
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            session.add(role)
        session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'default': self.default,
            'permissions': self.permissions,
            'users': [user.to_dict() for user in self.users]
        }
    
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm 

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm 

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm