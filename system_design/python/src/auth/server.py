import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

def createJWT(username, secret, isauthAdmin):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)+datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": isauthAdmin 
        },
        secret,
        algorithm="HS256"
    )

@server.route('/login', methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "Missing credentials", 401
    
    # check db for username and password
    curosr = mysql.connection.cursor()
    result = curosr.execure(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if result > 0:
        user_row = curosr.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "Invalid Credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "Invalid Credentials! User doesn't exist", 401
    
@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")

    if not encoded_jwt:
        return "Missing credentials", 401
    
    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return "Token expired", 403
    except jwt.InvalidTokenError:
        return "Not Authorized", 403

    return decoded, 200



if __name__ == "__main__":
    server.run(port=5000, host="0.0.0.0")