from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from cloudinary import CloudinaryImage
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import os
from config import Config
from bson.objectid import ObjectId

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(app.config['MONGO_URI'])
    db = client.wallmade
    return db

def get_collections():
    """Get all required collections"""
    db = get_db()
    return (
        db.products,
        db.works,
        db.users
    )

p,w,u=get_collections()
print(p,w,u)
print(list(p.find().limit(4)) )
