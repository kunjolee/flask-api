from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt

from sqlalchemy.exc import SQLAlchemyError

from schemas import ItemSchema, ItemUpdateSchema

from models import ItemModel

from db import db
#@blp.response is going to manage the main success response
blp = Blueprint('Items',__name__, url_prefix='/item', description='Operations on items')


@blp.route('/')
class itemsList(MethodView):
    #la respuesta va a ser convertida una lista de diccionarios con la estructura del schema ItemSchema
    @jwt_required()
    @blp.response(status_code=200, schema=ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
    # second parameter is going to contain the json payload (request values) validated, the fields that the schema specified.
    # the JSON that the client sends is passed through the ItemSchema, it checks that the fields and the valid types are there,etc. And then it gives the method an argument which is the validated dictionary "item_date"
    @jwt_required(fresh=True)
    @blp.arguments(schema=ItemSchema)
    @blp.response(status_code=201, schema=ItemSchema) 
    def post(self, item_data):        
        # json dictionary payload into keyword arguments and pass those arguments to the model 
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error ocurred while inserting item')
        
        return item


@blp.route('/<int:item_id>')
class Item(MethodView):
    # la respuesta tiene que tener la estructura de ItemSchema, no puedo devolver algo que no este en ese schema
    @jwt_required()
    @blp.response(status_code=200, schema=ItemSchema)
    def get(self,item_id):    
        item = ItemModel.query.get_or_404(item_id) # if founded returns item, or raise an abort 404
        return item

    @blp.arguments(schema=ItemUpdateSchema)
    @blp.response(status_code=200, schema=ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            # if the item exist update it
            item.price = item_data['price']
            item.name  = item_data['name'] 
        else:
            # if it doen't exist create an item with that id

            item = ItemModel(id=item_id, **item_data)
        
        db.session.add(item)
        db.session.commit()

        return item
    @jwt_required()
    def delete(self, item_id):
        if not get_jwt().get('is_admin'):
            abort(401, message='Admin privilege required')

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Item deleted'}