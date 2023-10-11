import typer
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.utils import hash
from app.models import Role, User
from app.database import get_db

cli = typer.Typer()

db: so.Session = next(get_db())

@cli.command()
def insert_roles():
    """Insert all roles in database"""
    db.execute(sa.delete(Role))
    Role.insert_roles(db)
    
    print("Roles added successfully!!!")

@cli.command()
def create_superuser(name: str, email: str, password: str):
    db.execute(sa.delete(User))
    role = db.scalars(sa.select(Role).where(Role.name == "Admin")).first()
    if role is None:
        print("Please insert roles first using: 'py manage.py insert-roles")
    else:
        
        admin = User(
            name=name, 
            email=email, 
            password=hash(password),
            role=role
        )
        db.add(admin)
        db.commit()
        print("Superuser created successfully!!!")

if __name__ == '__main__':
    cli()