"""
explanations:
create a virtual environment -> py -3 -m venv venv
activate the virtual environment in the terminal -> .\venv\Scripts\activate
starting the server using uvicorn -> uvicorn main:app --reload (with reload capabilities - this uses watchgod)
if two same routes are given in the decorators then the first match wins.
fastapi looks at two things - the method and the route.
what is the different b/w the post and get request
 - post - sneds the data to the server (allows us to that)
 - get - asks for some data from the server (not allowed to carry extra data with it)
we retrieve the data from the body  as argument provided.
"""
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
# from fastapi.params import Body
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
    published: bool = True #sets the default value to true.
    rating: Optional[int] = None #completely optional field of type integer.

# Making the database connection, the psycopg2 library helps us to connect and get the cursor.
# the library works in a similar way to sqlite library where we make the commits after every change.
# and there is a cursor for the current changes.
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='F0rgivene$$', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull!")
        break
    except Exception as e:
        print(f"Database connection failed \nerror: \n\n {e}")
        time.sleep(2)
# this is the path operation or the route
#  made of function and a decorator
# for the asynchronous task, we pass the async task
@app.get("/") #this decorator turns it into the path or fast api route, get method is for sending the get request at this route
def root():
    # this is the python dictionary but on the web browser it's a dictionary.
    return {"message": "Welcome to my api!"}

@app.get("/posts")
def get_posts():
    return {"message": my_posts}

@app.post("/posts", status_code= status.HTTP_201_CREATED)
# this is the extraction logic from the body, it converts the body into the dictionary and stores it in the payload
# def create_posts(payload: dict=Body(...)): #the body comes from the fastapi library
def create_posts(post: Post): #this is from the pydantic model and we have defined the class for the model above.
    # it automatically does the validation, for the required fields, datatype, etc.
    # print(payload)
    # print(post)
    # return {"new_post": f"title: {payload['title']} content: {payload['content']}"}
    # print ("new_post: ",  f"{post.dict()}")
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 9999999)
    my_posts.append(post_dict)
    # return {"new_post": f"{post.dict()}"}
    return {"data": f"{post_dict}"}
    # for a post request we want the title and the content, and they both are necessary.

@app.get('/posts/{id}') # the id field is also known as the path parameter
def get_post(id: int, response: Response): #internal checking by fastapi from string to int conversion.
    post = find_posts(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id:{id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND #if the post is not found, then send not found error.
        # return {"messsage": f"post with {id} was not found"}
    return {"post_detail": f"here is post : {post}"}

# the status 204 implicitly means that you are not meant to send any data back, hence we need to wrap the response object.
@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    #deleting post
    # find the index in the array that has the require id.
    # my_posts.pop(id)
    index = find_index_post(id)
    if(index == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id) #finds the index with the post with the specific id, so that it can be updated.
    if(index == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    my_posts.pop(index) #returns an exception if the post was not found in the data.
    post_dict = post.dict()
    post_dict['id'] = id #adds the id to the data, since externally there is no id passed.
    my_posts[index] = post_dict #the post is then updated by the converting the post to the dictionary format.
    return {'data': f"{post_dict} \nwas added"} #returns a success message