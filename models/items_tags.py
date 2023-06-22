# many-to-many relationship, a intermediate table to make the relation between tags and items

from db import db

class ItemsTagsModel(db.Model):
    __tablename__ = 'items_tags'

    id      = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    tag_id  = db.Column(db.Integer, db.ForeignKey('tags.id'))