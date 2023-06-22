from db import db

#lazy='dynamic': the items here are not going to be fetch from the db until we tell it to. 
class StoreModel(db.Model):
    __tablename__ = 'stores'
    # columns
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship('ItemModel', back_populates='store', lazy='dynamic', cascade='all, delete')
    tags  = db.relationship('TagModel', back_populates='store', lazy='dynamic')