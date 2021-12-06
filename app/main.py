"""
explanations:
create a virtual environment -> py -3 -m venv venv
activate the virtual environment in the terminal -> .\venv\Scripts\activate
starting the server using uvicorn -> uvicorn main:app --reload (with reload capabilities - this uses watchgod)

"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import user, post, auth, vote
from app.config import settings
app = FastAPI()

# Code for CORS policy, 
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def main():
    return {"message": "Hello World"}
# this is now dependent on the alembic migrations, and it creates the tables automatically.
# however, in case the alembic is not present, the tables are not going to make themselves and we need to run the setup engine.
# models.Base.metadata.create_all(bind=engine)

@app.get("/") 
def root():
    return {"message": "Welcome to my api!"}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


