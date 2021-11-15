"""
explanations:
create a virtual environment -> py -3 -m venv venv
activate the virtual environment in the terminal -> .\venv\Scripts\activate
starting the server using uvicorn -> uvicorn main:app --reload (with reload capabilities - this uses watchgod)

"""
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
import time
from . import models
from .database import engine
from .routers import user, post, auth



app = FastAPI()

models.Base.metadata.create_all(bind=engine)

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='F0rgivene$$', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull!")
        break
    except Exception as e:
        print(f"Database connection failed \nerror: \n\n {e}")
        time.sleep(2)

@app.get("/") 
def root():
    return {"message": "Welcome to my api!"}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


