from os import path

from peewee import SqliteDatabase, Model, PrimaryKeyField, CharField, BigIntegerField, TextField, IntegerField

from modules.config import config
from modules.types import AddressState

db = SqliteDatabase(config['db']['path'])


class BaseModel(Model):
    class Meta:
        database = db


class Address(BaseModel):
    id = PrimaryKeyField()
    uuid = CharField(43, unique=True)
    url = TextField()
    aes_key = TextField()
    state = IntegerField(default=AddressState.Active)
    created_at = BigIntegerField()
    expired_at = BigIntegerField(default=0)


def init_db():
    if path.exists(config['db']['path']):
        return

    db.connect()
    db.create_tables([Address])
    db.close()
