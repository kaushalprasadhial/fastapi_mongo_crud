from pymongo import MongoClient
import gridfs

conn = MongoClient()
fs = gridfs.GridFS(conn.testing)