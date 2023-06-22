import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db
import models
from blocklist import BLOCKLIST

from resources.item import blp as Items
from resources.store import blp as Stores
from resources.tag import blp as Tags
from resources.user import blp as Users

def create_app(db_url=None):
    app = Flask(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['API_TITLE']  = 'Stores REST API'
    app.config['API_VERSION']= 'v1'
    app.config['OPENAPI_VERSION']= '3.0.3'
    app.config['OPENAPI_URL_PREFIX']= '/'
    app.config['OPENAPI_SWAGGER_UI_PATH']='/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL']='https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

    # connection to DB
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # initialize DB
    db.init_app(app=app) 

    with app.app_context():
        # Create tables defined by models if not exists. SQLALCHEMY knows what table to crete becase we import models on line 6 otherwise SQLAlchemy will not know from which model create the tables
        db.create_all()

    # connect JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_JWT')
    jwt = JWTManager(app=app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        # whenever we receive a JWT this function runs. jti is the unique id of the jwt
        return jwt_payload['jti'] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        # it will be sent to the client when check_if_token_in_blocklist() returns true
        return (
            jsonify(
                {'description': 'the token has been revoked', 'error': 'token revoked'}
            ),
            401
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify({'description': 'The token is not fresh.', 'error': 'fresh_token_required'}),
            401
        )

    @jwt.additional_claims_loader
    def add_claim_to_jwt(identity):
        # claims add info to jwt payload
        if identity == 1:
            return {'is_admin': True}
        return {'is_admin': False}

    @jwt.expired_token_loader
    def expired_token_loader(jwt_header, jwt_payload):
        # the function should return the tuple with the json and the status code
        return (
            jsonify({'message': 'The token has expired.', 'error': 'token_expired'}),
            401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({'message': 'Signature verification failed', 'error': 'invalid_token'}),
            401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify({'description': 'Request does not contain an access token.', 'error': 'authorization required'}),
            401
        )

    # Connect flask app to flask smorest
    api = Api(app=app)

    
    api.register_blueprint(Items)
    api.register_blueprint(Stores)
    api.register_blueprint(Tags)
    api.register_blueprint(Users)
    
    return app