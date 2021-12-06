from os import stat
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND
from app import schemas, database, models, oauth2
router = APIRouter(prefix="/vote", tags = ["vote"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user = Depends(oauth2.get_current_user)):
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    # if the post on which the user likes does not exist then there will be error and it should say 404 not found.
    # logic is implemented here.
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {vote.post_id} does not exist")
    
    # if vote is plus
    if(vote.dir == 1):
        # if the vote already exist raise an HTTP exception fo conflict with the already present data..
        # else add a new vote to the database.
        if(found_vote):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User {current_user.id} has already voted on the post {vote.post_id}" )
        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "successfully added vote"}
    else:
        # if the vote id down
        # if the vote is not found then return an error of no existing vote and can't delete it.
        # else delete the vote, and commit to the database.
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "vote does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "succesfully deleted vote"}
