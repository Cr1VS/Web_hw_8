from mongoengine import (
    Document,
    StringField,
    ReferenceField,
    ListField,
    CASCADE,
    BooleanField,
    DateTimeField,
)
from bson import ObjectId


class Author(Document):
    fullname = StringField(required=True, unique=True)
    born_date = StringField(max_length=50)
    born_location = StringField(max_length=150)
    description = StringField()
    meta = {"collection": "authors"}


class Quote(Document):
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    tags = ListField(StringField(max_length=50))
    quote = StringField()
    meta = {"collection": "quotes"}


class Contact(Document):
    fullname = StringField()
    email = StringField()
    phone_num = StringField()
    logic_field = BooleanField(default=False)
    date_of = DateTimeField()
