import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_service import access
from storage import util

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.router("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    access = json.loads(access)
    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "Exactly 1 file required", 400
        for key, value  in request.files.items():
            error = util.upload(file, gridfs_instance, rabbitmq_channel, access)   

            if error:
                return error
        return "Success!", 200
    else:
        return "Not authorized", 401

@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=80)