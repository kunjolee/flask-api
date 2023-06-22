from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST

blp = Blueprint('Users', __name__, description='Operations on users')

@blp.route('/register')
class UserRegister(MethodView):

    @blp.arguments(schema=UserSchema)
    def post(self, user_data):
        """
        user_data: data coming from the request (passed through @blp.arguments decorator)
        """
        if UserModel.query.filter( UserModel.username == user_data['username'] ).first():
            abort(409, message='A user with that username already exists. ')


        user = UserModel(
            username=user_data['username'],
            password= pbkdf2_sha256.hash(user_data['password'])
        )

        db.session.add(user)
        db.session.commit()

        return {'message': 'User created successfully'}


@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data['username']
        ).first()

        # we will need a fresh token to delete an account, we might ask the user to login again, but if we just want to see our posts, we can use a non fresh token
        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True) 
            refresh_token = create_refresh_token(identity=user.id )
            return {'access_token': access_token, 'refresh_token': refresh_token }
        
        abort(401, message='Invalid credentials.')


@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti'] #.get is not necessary because jti is always going to be in the jwt
        BLOCKLIST.add(jti)
        return {'message': 'Successfully logged out'}

@blp.route('/refresh')
class TokenRefresh(MethodView):
    @jwt_required(refresh=True) #requires a refresh token to access this token
    def post(self):
        current_user = get_jwt_identity()
        # whenever the client call this endpoints it requires a refresh token and this will generate a non fresh token using fresh=False
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {"access_token": new_token}

@blp.route('/user/<int:user_id>')
class User(MethodView):

    @blp.response(status_code=200, schema=UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {'message': 'User deleted'}, 200

# Login