from config.db import conn


all_users = conn.testing.user.find()

for user in all_users:
    conn.testing.user.find_one_and_delete({"_id":user['_id']})

all_files = conn.testing.fs.files.find()
for file in all_files:
    conn.testing.fs.files.find_one_and_delete({"_id":file['_id']})

all_chunks = conn.testing.fs.chunks.find()
for chunk in all_chunks:
    conn.testing.fs.chunks.find_one_and_delete({"_id":chunk['_id']})