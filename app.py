import os
from flask import Flask
from flask_restful import Api
from resources import Twitter


app=Flask(__name__)


api=Api(app)


@app.route("/")
def home():
    return "<h1 style='color:blue'>This is the Twitter User  pipeline!</h1>"


api.add_resource(Twitter, '/twitter/')

if __name__=='__main__':
    app.run(host='0.0.0.0')
