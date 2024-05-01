from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
from sqlalchemy.orm import Session
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
from .database import engine, SessionLocal
import time 

models.Base.metadata.create_all(bind=engine)
# create instance
app = FastAPI()

#
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#define Class as chame for Database to make sure data match database type
class Post(BaseModel):
    title: str   
    content: str
    published: bool=True
    rating: Optional[int] = None

#get connection
while True:
    try:
        conn = psycopg2.connect(host='localhost', port='5432' ,database='fastapi', user='root', password='root',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Databse connected !!!')
        break
    except Exception as error:
        print('connection fail !')
        print("Error : ",error)
        time.sleep(2)
    
        
@app.get("/")
async def root():
    return {"message": "REST API TEST"}

@app.get("/sqlalchemy")
async def test_posts(db:Session=Depends(get_db)):
    return {"status":"success"}
    

@app.get("/posts")
async def get_posts():
    cursor.execute('''  SELECT * FROM posts''')
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}

@app.get("/posts/{id}")
async def get_post(id:int):
    #find id , id need back to string to work on SQL
    cursor.execute(f"SELECT * FROM posts WHERE id ={id} " )
    post = cursor.fetchone()
    print(post)
    # No post found
    if not post :
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post_id {id} was not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post_id {id} was not found"}
    return {"msg":post}

#create
# modify status code
@app.post("/posts")
async def create_posts(post:Post = Body(...),status_code = status.HTTP_201_CREATED):
    cursor.execute(""" INSERT INTO posts (title,content,published)
                       VALUES (%s,%s,%s) RETURNING *""",
                       (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"message": new_post} 

#delete
@app.delete("/posts/{id}")
async def del_post(id:int,status_code = status.HTTP_204_NO_CONTENT):
    cursor.execute(f"DELETE FROM posts WHERE id={id} RETURNING *")
    deleted_post = cursor.fetchone()
    conn.commit()  #close database
    
    if deleted_post is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post_id {id} not found")
    
    return Response(status_code = status.HTTP_204_NO_CONTENT)

#update
@app.put("/posts/{id}")
async def update_post(id:int,post:Post):
    cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
                   (post.title,post.content,post.published,id),)
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail =f"post with {id} does not exist")
    
    return {"data":updated_post}