from sqlalchemy import Table, Column, Integer, JSON, MetaData, ForeignKey
from auth.models import user

metadata = MetaData()

mushroom = Table(
     "mushroom",
     metadata,
     Column("id", Integer, ForeignKey(user.c.id)),
     Column("Info", JSON, nullable=False)
 )



