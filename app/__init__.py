from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine
from .config import Config
from azure.storage.blob import BlobServiceClient
from .models import User
from app import routes
from flask_cors import CORS
from .models.db import db
from database import seed_database
import os
import jwt

app = Flask(__name__)
migrate = Migrate(app, db)
jwt_manager = JWTManager(app)
CORS(app)
app.config.from_object(Config)
# Access Azure Storage configuration
storage_account_name = app.config["AZURE_STORAGE_ACCOUNT_NAME"]
storage_account_key = app.config["AZURE_STORAGE_ACCOUNT_KEY"]
container_name = app.config["AZURE_CONTAINER_NAME"]

# Use these values when establishing a connection to Azure Storage
blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=storage_account_key)
container_client = blob_service_client.get_container_client(container_name)


app.config['CACHE_TYPE'] = 'simple'  # Use a simple in-memory cache
cache = Cache(app)

@app.route('/api/config')
@cache.cached(timeout=3600)
def get_config():
    api_key = os.environ.get('API_KEY')
    return jsonify({'api_key': api_key})

@app.route('/protected', methods=['GET'])
def protected_route():
    access_token_cookie = request.cookies.get('access_token')
    if access_token_cookie:
        try:
            # Decode the access token from the cookie
            decoded_token = jwt.decode(
            access_token_cookie, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = decoded_token.get('username')
            id = decoded_token.get('id')
            user_instance = User.query.get(id)
            user_info = user_instance.to_dict()

            # Authentication successful, respond with data from the protected endpoint
            return jsonify({
                'user': user_info
            }), 200
        except jwt.ExpiredSignatureError:
            # Token has expired, respond with unauthorized status code
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            # Invalid token, respond with unauthorized status code
            return jsonify({'message': 'Invalid token'}), 401
    else:
        return jsonify({'message': 'Access token not found'}), 401

routes_list = [
    routes.main.bp,
    routes.matches.bp,
    routes.match.bp,
    routes.news.bp,
    routes.auth.bp,
    routes.league.bp,
    routes.club.bp,
    routes.player.bp,
    routes.post.bp,
    routes.like.bp,
    routes.comment.bp,
    routes.notification.bp,
    routes.repost.bp,
    routes.user.bp,
    routes.standings.bp,
    routes.favorite.bp
]

for route in routes_list:
  app.register_blueprint(route)

db.init_app(app)
# seed_database(app)

# engine = create_engine(db_url)

if __name__ == '__main__':
    app.run(port=5000, debug=True)