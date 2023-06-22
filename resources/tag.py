from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import StoreModel, TagModel, ItemModel, ItemsTagsModel
from schemas import TagSchema, TagAndItemSchema


blp = Blueprint('tag', __name__, description='Operations on tag')

@blp.route('/store/<int:store_id>/tag')
class TagsInStore(MethodView):
    @blp.response(status_code=200, schema=TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()
        
    
    @blp.arguments(schema=TagSchema)
    @blp.response(status_code=201, schema=TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(  TagModel.store_id == store_id, TagModel.name == tag_data['name'] ).first():
            abort(400, message='Tag with that name already exist in that store')

        tag = TagModel(name=tag_data['name'], store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
            
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag
    

@blp.route('/tag/<int:tag_id>')
class Tag(MethodView):
    # get specific tag
    @blp.response(status_code=200, schema=TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    # for documentation purposes
    @blp.response(status_code=202, description='Deletes a tag if not item is tagged with it', example={'message': 'Tag deleted'})
    @blp.alt_response(status_code=404, description='Tag not found.')
    @blp.alt_response(status_code=400, description='Returned if the tag is assigned to one or more items. in this case, the tag is not deleted.')
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        # si no hay items en relacionados en este tag
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()

            return {'message': 'Tag deleted'}

        # si hay algun item relacionado a este tag, significa que no lo puedo eliminar
        abort(400, message='Could not deleted tag. make sure tag is not associated with any items, then try again.')

# linked with items
@blp.route('/item/<int:item_id>/tag/<int:tag_id>')
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        
        item = ItemModel.query.get_or_404(item_id)
        tag  = TagModel.query.get_or_404(tag_id)

        if item.store_id != tag.store_id:
            abort(404, message='You can not link a tag from a certain store with an item from a different store')

        item.tags.append(tag)
        # tag.items.append(item) -> it can be this way too, appending items to tag or viceversa like above

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error ocurred while inserting the tag.')

        return tag
    
    # remove an item from tag
    @blp.response(status_code=200, schema=TagAndItemSchema)
    def delete(self, item_id, tag_id):
        # if TagModel.query.filter( TagModel.items.id != item_id, TagModel.id != tag_id ):
        
        if ItemsTagsModel.query.filter( ItemsTagsModel.item_id != item_id, ItemsTagsModel.tag_id != tag_id).first():            
            abort(400,message='Item not in tag')

        item = ItemModel.query.get_or_404(item_id)
        tag  = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error ocurrer while deleting the tag.')

        return {'message': 'Item removed from tag', 'item': item, 'tag': tag}