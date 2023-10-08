from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {
        "message": "Welcome to Locallibrary-FastAPI"
    }

# for admin use only
# @click.command()
# def create_roles():
#     models.Role.insert_roles(session=database.Session())
#     print("Roles successfully created")