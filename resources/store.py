# Method view hace que los nombres de los metodos hagan referencia a su respectivo http methos. e.g el metodo get dentro de la clase va a ejecutarse al momento de usar el metodo get en la peticion (postman, client, etc)

from uuid import uuid4
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoreSchema
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db import db
from models import StoreModel

blp = Blueprint('stores', __name__, url_prefix='/store' , description='Operations on stores')

@blp.route('/')
class StoreList(MethodView):
    @blp.response(status_code=200, schema=StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(schema=StoreSchema)
    @blp.response(status_code=201, schema=StoreSchema)
    def post(self, store_data):
        store = StoreModel(name=store_data['name'])
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message='A store with that name already exist')
        except SQLAlchemyError:
            abort(500, message='An error ocurred creating the store.')
        return store
    
@blp.route('/<int:store_id>')
class Store(MethodView):
    @blp.response(status_code=200, schema=StoreSchema)
    def get(self, store_id):
        my_store = StoreModel.query.get_or_404(store_id)
        return my_store
    
    def delete(self, store_id):
        my_store = StoreModel.query.get_or_404(store_id)
        db.session.delete(my_store)
        db.session.commit()
        return {"message": "Store deleted"}

