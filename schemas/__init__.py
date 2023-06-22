# Write marshmallow schemas for stores and items validations

from marshmallow import Schema, fields

# items
class PlainItemSchema(Schema):
    id    = fields.Int(dump_only=True) 
    name  = fields.Str(required=True)
    price = fields.Float(required=True)

# stores
class PlainStoreSchema(Schema):
    id   = fields.Int(dump_only=True)
    name = fields.Str(required=True)

# tags
class PlainTagSchema(Schema):
    id   = fields.Int(dump_only=True)
    name = fields.Str(required=True)

# update item
class ItemUpdateSchema(Schema):
    name     = fields.Str(required=True)
    price    = fields.Float(required=True)
    store_id = fields.Int()

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True) #only when receiving data from client (json payload)
    store    = fields.Nested(PlainStoreSchema(), dump_only=True) # Return data to the client
    tags     = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class StoreSchema(PlainStoreSchema):   
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True) 
    tags  = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class TagSchema(PlainTagSchema):
    # store_id = fields.Int(required=True, load_only=True)
    items     = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    store    = fields.Nested(PlainStoreSchema(), dump_only=True)
    

class TagAndItemSchema(Schema):
    message = fields.Str()
    item    = fields.Nested(ItemSchema)
    tag     = fields.Nested(TagSchema)


# users
class UserSchema(Schema):
    id       = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True) # the password will never be sent to the client

# dumb_only: the field will only be used to send data back to the client in the response. and it will be ignored in the json payload (the request)