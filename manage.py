import typer
import sqlalchemy as sa
import sqlalchemy.orm as so
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
    roles = db.scalars(sa.select(Role).order_by(Role.name.asc())).all()
    if len(roles) == 0:
        print("Please insert roles first using: 'py manage.py insert-roles")
    else:
        
        admin = User(
            name=name, 
            email=email, 
            password=password,
            role=roles[0]
        )
        db.add(admin)
        db.commit()
        print("Superuser created successfully!!!")

if __name__ == '__main__':
    cli()