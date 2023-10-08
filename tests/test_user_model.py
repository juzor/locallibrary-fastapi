import pytest
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import User, Role, Permission

def test_roles(test_roles):

    assert len(test_roles) == 3

def test_user_not_valid(session):
    user = User()
    assert user.name is None
    assert user.password is None
    assert user.email is None
    assert user.role is None

def test_user_is_patron(session, test_roles):
    user = User(
        name='Fimba Limba',
        password='wakanda',
        email='fimba.limba@email.com',
        role=test_roles[2]
    )
    session.add(user)
    session.commit()
    u = session.scalar(sa.select(User).where(User.name == user.name))

    assert u is not None
    assert u == user
    assert u.role.permissions == 31
    assert u.role.name == 'Patron'
    assert u.can(Permission.BORROW)
    assert u.can(Permission.RENEW)
    assert u.can(Permission.RETURN)
    assert u.can(Permission.PAY_FINES)
    assert u.can(Permission.RESERVE)
    assert not u.can(Permission.ADD_NEW_BOOK)
    assert not u.can(Permission.REMOVE_BOOK)

def test_user_is_librarian(session, test_roles):
    u = User(
        name='Da Librarian',
        password='wakanda',
        email='lbrarian@email.com',
        role=test_roles[1]
    )
    session.add(u)
    session.commit()

    assert u is not None
    assert u.role.permissions == 127
    assert u.role.name == 'Librarian'
    assert u.can(Permission.BORROW)
    assert u.can(Permission.RENEW)
    assert u.can(Permission.RETURN)
    assert u.can(Permission.PAY_FINES)
    assert u.can(Permission.RESERVE)
    assert u.can(Permission.ADD_NEW_BOOK)
    assert u.can(Permission.REMOVE_BOOK)

def test_user_is_admin(session, test_roles):
    u = User(
        name='Admin Dada',
        password='wakanda',
        email='admin@email.com',
        role=test_roles[0]
    )
    session.add(u)
    session.commit()

    assert u is not None
    assert u.role.permissions == 511
    assert u.role.name == 'Admin'
    assert u.can(Permission.BORROW)
    assert u.can(Permission.RENEW)
    assert u.can(Permission.RETURN)
    assert u.can(Permission.PAY_FINES)
    assert u.can(Permission.RESERVE)
    assert u.can(Permission.ADD_NEW_BOOK)
    assert u.can(Permission.REMOVE_BOOK)
    assert u.can(Permission.SUSPEND_USER)
    assert u.can(Permission.ADMIN)

