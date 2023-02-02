from fastapi import APIRouter, Depends, File, UploadFile, Response, HTTPException
from starlette.responses import StreamingResponse
from typing import List
from PIL import Image
import io
from models.user import User, Base 
from config.db import conn, fs
from schemas.user import serializeDict, serializeList, get_image
from bson import ObjectId
user = APIRouter() 

# @user.get('/')
# async def find_all_users():
#     return serializeList(conn.testing.user.find())

@user.get('/{id}')
async def find_one_user(id):
    user = conn.testing.user.find_one({"_id":ObjectId(id)})
    if user is not None:
        print(f"user {user}")
        file = fs.find_one({'_id':ObjectId(user['image_id'])})
        if file is None:
            print('no file')
        async def chunk_generator(grid_out):
            while True:
                chunk = grid_out.readchunk()
                if not chunk:
                    break
                yield chunk
        users_data = {**{i:str(user[i]) for i in user if i=='_id'},
                **{i:user[i] for i in user if i!='_id'}}
        return StreamingResponse(content = chunk_generator(file), headers = users_data, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="user not found")

@user.put('/{id}')
async def update_user(id,user: User):
    conn.testing.user.find_one_and_update({"_id":ObjectId(id)},{
        "$set":dict(user)
    })
    return serializeDict(conn.testing.user.find_one({"_id":ObjectId(id)}))

@user.delete('/{id}')
async def delete_user(id,user: User):
    user = conn.testing.user.find_one_and_delete({"_id":ObjectId(id)})
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    file = conn.testing.fs.files.find_one_and_delete({"_id":ObjectId(user['image_id'])})
    if file is not None:
        all_chunks = conn.testing.fs.chunks.find({"files_id":ObjectId(file['_id'])})
    print(f"all_chunks {all_chunks}")
    # print(f'len(all_chunks) {len(all_chunks)}')
    count = 0
    for chunk in all_chunks:
        count+=1
        conn.testing.fs.chunks.find_one_and_delete({"_id":chunk['_id']})
    
    print(f"user {user}\n total chunks deleted {count}")
    return serializeDict(user)

@user.post("/create_user")
async def create_user(user: User = Depends(), file: UploadFile = File(...)):
    user_data = dict(user)
    filename = file.filename
    id = fs.put(file.file, filename=filename)
    user_data['image'] = filename
    user_data['image_id'] = str(id)
    conn.testing.user.insert_one(user_data)
    return_data = {key:user_data[key] for key in user_data.keys() if key!='_id'}
    return return_data
    