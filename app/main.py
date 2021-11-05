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
    return {"data": f"{new_post}"}

@app.get('/posts/{id}')
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id= %s """, (id))
    test_post = cursor.fetchone()
    post = find_posts(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id:{id} was not found")
    return {"post_detail": f"here is post : {test_post}"}

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if(index == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if(index == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    my_posts.pop(index)
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict 
    return {'data': f"{post_dict} \nwas added"} 