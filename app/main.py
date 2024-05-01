from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2

# create instance
app = FastAPI()

#define Class as chame for Database to make sure data match database type
class Post(BaseModel):
    title: str   
    content: str
    published: bool=True
    rating: Optional[int] = None

#get connection

# like cache   
my_posts =[
    {"title":"title 1", "content":"content 1", "id":0},
    {"title":"title 2", "content":"content 2", "id":1}
]
def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p 

def find_index_id(id):
    for i,p in enumerate(my_posts): #as list
        if p['id'] == id :
            return i
        
@app.get("/")
async def root():
    return {"message": "REST API TEST"}

@app.get("/posts")
async def get_posts():
    return {"data": my_posts}

@app.get("/posts/{id}")
async def get_post(id:int,response:Response):
    print(id)
    print(type(id))
    post = find_post(int(id))
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
    id = 1
    # append new post
    post_dict = post.model_dump()
    post_dict['id'] = id + 1
    my_posts.append(post_dict)
    return {"message": f"successfully "} 

#delete
@app.delete("/posts/{id}")
async def del_post(id:int,status_code = status.HTTP_204_NO_CONTENT):
    index = find_index_id(id)
    if index is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post_id {id} not found")
    my_posts.pop(index)
    return Response(status_code = status.HTTP_204_NO_CONTENT)

#update
@app.put("/posts/{id}")
async def update_post(id:int,post:Post):
    index = find_index_id(id)
    if index is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND)
    print(post)
    # convert into dict
    post_dict = post.model_dump()
    #add id to the obj/dict
    post_dict['id'] = id
    #replace obj in the index
    my_posts[index] = post_dict
    return {"data":post_dict}