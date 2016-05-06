#!/usr/bin/python

import sys, os, logging

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "copyThat"
    )
)

#from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.sql.expression as ex
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, String, DateTime, Enum, Numeric, Index, ForeignKeyConstraint, UniqueConstraint

# DateTime, Enum('a', 'b', 'c'), Numeric(10, 2), ForeignKey('user.id')

# for table in $(sqlite3 /tmp/db.sqlite '.tables'); do sqlite3 /tmp/db.sqlite ".dump $table"; donea

# select([sometable]).where(sometable.c.column.like("%foobar%"))

os.remove('/tmp/db.sqlite')
engine = create_engine('sqlite:////tmp/db.sqlite')


# pk = primary key
# ix = index
# uq = unique
# fk = foreign
# ck = check

metadata = MetaData()


classes = Table(
    "classes",
    metadata,
    Column("class_id", Integer, primary_key=True, autoincrement=True),
    Column("class_namespace", String(255), nullable=False),
    Column("class_name", String(255), nullable=False),
    UniqueConstraint("class_namespace", "class_name", name="uq_classname"),
)

classattributes = Table(
    "classattributes",
    metadata,
    Column("class_id", primary_key=True, autoincrement=False),
    Column("attr_key", String(255), primary_key=True),
    Column("attr_name", String(255), nullable=False),
    Column("attr_type", Enum('string', 'int', 'bool', 'float', 'json'), nullable=False),
    Column("attr_default", String(255)),
    ForeignKeyConstraint(["class_id"], ["classes.class_id"], name="fk_objectclass1", ondelete="CASCADE", onupdate="CASCADE"),
)

objects = Table(
    "objects",
    metadata,
    Column("object_id", Integer, primary_key=True, autoincrement=True),
    Column("object_name", String(255), nullable=False),
    Column("object_subname", String(255)),
    Column("class_id", Integer, nullable=False),
    UniqueConstraint("object_name", "object_subname", "class_id", name="uq_objectname"),
    Index("ix_objectclass", "class_id"),
    ForeignKeyConstraint(["class_id"], ["classes.class_id"], name="fk_objectclass2", ondelete="CASCADE", onupdate="CASCADE"),
)

objectattributes = Table(
    "objectattributes",
    metadata,
    Column("object_id", Integer, primary_key=True, autoincrement=False),
    Column("class_id", Integer, primary_key=True),
    Column("attr_key", String(255), primary_key=True),
    Column("attr_value", Text),
    Index("ix_attrKey", "attr_key"),
    ForeignKeyConstraint(["object_id", "class_id"], ["objects.object_id", "objects.class_id"], name="fk_objects", ondelete="CASCADE", onupdate="CASCADE"),
    ForeignKeyConstraint(["class_id", "attr_key"], ["classattributes.class_id", "classattributes.attr_key"], name="fk_classattributes", ondelete="CASCADE", onupdate="CASCADE"),
)

metadata.create_all(engine)

conn = engine.connect()

# Inserting Claasses
conn.execute(classes.insert().values({"class_namespace": "Indexes", "class_name": "Indexes"}))
conn.execute(classes.insert().values({"class_namespace": "Apps",    "class_name": "Apps"}))

# Inserting ClassAttributes for Indexers
result = conn.execute((classes.select().where(classes.c.class_namespace=="Indexes" and classes.c.class_name=="Indexes"))).fetchone()
conn.execute(classattributes.insert().values({"class_id": result.class_id, "attr_key": "IndexOwner", "attr_name": "Splunk Index Owner", "attr_type": "string"}))
conn.execute(classattributes.insert().values({"class_id": result.class_id, "attr_key": "DataSensitive", "attr_name": "Data Sensitive", "attr_type": "bool", "attr_default": "False"}))
conn.execute(classattributes.insert().values({"class_id": result.class_id, "attr_key": "TargetedUsers", "attr_name": "Targeted Users", "attr_type": "string"}))
conn.execute(classattributes.insert().values({"class_id": result.class_id, "attr_key": "TargetedGroups", "attr_name": "Targeted Groups", "attr_type": "string"}))
conn.execute(classattributes.insert().values({"class_id": result.class_id, "attr_key": "IndexedGBPerDay", "attr_name": "GB per Day", "attr_type": "float"}))

# Inserting ClassAttributes for Apps
result = conn.execute((classes.select().where(classes.c.class_namespace=="Apps" and classes.c.class_name=="Apps"))).fetchone()
conn.execute(classattributes.insert().values({"class_id": result.class_id, "attr_key": "AppOwner", "attr_name": "Splunk App Owner", "attr_type": "string"}))
conn.execute(classattributes.insert().values({"class_id": result.class_id, "attr_key": "TargetedUsers", "attr_name": "Targeted Users", "attr_type": "string"}))
conn.execute(classattributes.insert().values({"class_id": result.class_id, "attr_key": "TargetedGroups", "attr_name": "Targeted Groups", "attr_type": "string"}))


result = conn.execute(ex.select([classes.c.class_namespace, classes.c.class_name, classattributes]).select_from(ex.join(classattributes, classes, classattributes.c.class_id == classes.c.class_id)))
for row in result:
   print(row)
   ii = 0
   for i in result._cursor_description():
       print("\t" + str(i[0]) + " = " + str(row[ii]))
       ii = ii + 1


