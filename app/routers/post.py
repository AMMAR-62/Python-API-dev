from typing import List,Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.sql.sqltypes import String
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
# testing the sqlalchemy orm, Session is imported from the sqlalchemy ORM, and Depends is imported from fastapi..
# this is more of a copy paste, and one time mechanism, and not to be confused, some terms must be kept in mind though.
# @router.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
#     post = db.query(models.Post).all()
#     return {"data" : post}
router = APIRouter( prefix="/posts", tags=['Posts'])
@router.get("/", response_model = List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user), Limit: int= 10, Off: int = 0, Search: Optional[str] = ""):
    # cursor.execute("SELECT * FROM posts")
    # posts = cursor.fetchall()
    post = db.query(models.Post).filter(models.Post.title.contains(Search)).limit(Limit).offset(offset=Off).all()
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).all()
    # post = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    return results

@router.post("/", status_code= status.HTTP_201_CREATED, response_model = schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user)): 
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published)) #this makes sure that we are not vulnerable to sql injection.
    # new_post = cursor.fetchone()
    # conn.commit() 
    # new_post = models.Post(title= post.title, content = post.content, published = post.published) #This can't always be done, as they may be enormous no. of fields for a table, so we unpack the pydantic model, by first converting it into the dictionary.
    new_post = models.Post(owner_id = current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post) #this is equivalent to RETURNING *
    return new_post

# get post with an id
@router.get('/{id}', response_model = schemas.Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id= %s """, (str(id),)) #int object does not support indexing, we convert it into string and not the argument so that the user can pass it as integer, 
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with id:{id} was not found")
    # if(post.owner_id != current_user.id): 
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform the requested action")
    return post

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit() # we commit to the connection and not the cursor.
    post_query = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = post_query.first()
    if(deleted_post == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    if(deleted_post.owner_id != current_user.id): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform the requested action")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model = schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title= %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # updated_posts = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if(updated_post == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    if(updated_post.owner_id != current_user.id): 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not authorized to perform the requested action")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return updated_post