import mongoengine as me

class Products(me.Document):
    title = me.StringField(required=True)
    barcode = me.StringField()
    meta = {'collection': 'products'}