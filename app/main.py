"""
explanations:
create a virtual environment -> py -3 -m venv venv
activate the virtual environment in the terminal -> .\venv\Scripts\activate
starting the server using uvicorn -> uvicorn main:app --reload (with reload capabilities - this uses watchgod)

"""
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException

from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time



app = FastAPI()

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favourite foods", "content": "I like pizza", "id": 2}]

def find_posts(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

class Post(BaseModel):
    title: str
    content: str
    published: bool = True 
    rating: Optional[int] = None 

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

@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code= status.HTTP_201_CREATED)

def create_posts(post: Post): 
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published)) #this makes sure that we are not vulnerable to sql injection.
    new_post = cursor.fetchone()
    conn.commit() 
    return f"{new_post}"

# get post with an id
@app.get('/posts/{id}')
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id= %s """, (str(id),)) #int object does not support indexing, we convert it into string and not the argument so that the user can pass it as integer, 
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id:{id} was not found")
    return f"{post}"

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit() # we commit to the connection and not the cursor.
    if(deleted_post == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title= %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    updated_posts = cursor.fetchone()
    conn.commit()
    if(updated_posts == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")

    return f"{updated_posts}"