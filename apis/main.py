from flask import Flask
import redis
import os
#from flask_cors import CORS, cross_origin

global redisClient
redisClient = redis.Redis(host=(os.environ['REDIS_HOST']),
password=(os.environ['REDIS_PASSWORD']),
port=(os.environ['REDIS_PORT']),
decode_responses=True)

app = Flask(__name__)
#cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'

# the minimal Flask application
@app.route('/getAllReviews')
#@cross_origin()
def say_hello():
    try:
        global redisClient
        # get all review data from redis
        data = redisClient.hgetall("tvReview")
        print("redis data",data)
        return data;
    except (IndexError, ValueError):
        print(ValueError)
        return []

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))