"""
explanations:
create a virtual environment -> py -3 -m venv venv
activate the virtual environment in the terminal -> .\venv\Scripts\activate
starting the server using uvicorn -> uvicorn main:app --reload (with reload capabilities - this uses watchgod)

"""
from typing import List
from fastapi import FastAPI, Response, status, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session

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

# testing the sqlalchemy orm, Session is imported from the sqlalchemy ORM, and Depends is imported from fastapi..
# this is more of a copy paste, and one time mechanism, and not to be confused, some terms must be kept in mind though.
# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
#     post = db.query(models.Post).all()
#     return {"data" : post}

@app.get("/posts", response_model = List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("SELECT * FROM posts")
    # posts = cursor.fetchall()
    post = db.query(models.Post).all()
    return post

@app.post("/posts", status_code= status.HTTP_201_CREATED, response_model = schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)): 
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published)) #this makes sure that we are not vulnerable to sql injection.
    # new_post = cursor.fetchone()
    # conn.commit() 
    # new_post = models.Post(title= post.title, content = post.content, published = post.published) #This can't always be done, as they may be enormous no. of fields for a table, so we unpack the pydantic model, by first converting it into the dictionary.
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post) #this is equivalent to RETURNING *
    return new_post

# get post with an id
@app.get('/posts/{id}', response_model = schemas.Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id= %s """, (str(id),)) #int object does not support indexing, we convert it into string and not the argument so that the user can pass it as integer, 
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id:{id} was not found")
    return post

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit() # we commit to the connection and not the cursor.
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if(deleted_post.first() == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", response_model = schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title= %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # updated_posts = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if(post_query.first() == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()