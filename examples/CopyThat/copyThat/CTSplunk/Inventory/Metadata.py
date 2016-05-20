from sqlalchemy import create_engine, MetaData, Table, Column, Boolean, Integer, Text, String, DateTime, Enum, Numeric, Index, ForeignKeyConstraint, UniqueConstraint

# Convention for keys:
# pk = primary key
# ix = index
# uq = unique
# fk = foreign
# ck = check

InventoryMetadata = MetaData()


InventoryClasses = Table(
    "invclasses",
    InventoryMetadata,
    Column("class_id", Integer, primary_key=True, autoincrement=True),
    Column("class_namespace", String(255), nullable=False),
    Column("class_name", String(255), nullable=False),
    UniqueConstraint("class_namespace", "class_name", name="uq_classname"),
)

InventoryClassAttributes = Table(
    "invclassattributes",
    InventoryMetadata,
    Column("class_id", primary_key=True, autoincrement=False),
    Column("attr_key", String(255), primary_key=True),
    Column("attr_name", String(255), nullable=False),
    Column("attr_type", Enum('string', 'int', 'bool', 'float', 'json'), nullable=False),
    Column("attr_default", String(255)),
    Column("attr_mandatory", Boolean, default=True),
    ForeignKeyConstraint(["class_id"], ["invclasses.class_id"], name="fk_objectclass1", ondelete="CASCADE", onupdate="CASCADE"),
)

InventoryObjects = Table(
    "invobjects",
    InventoryMetadata,
    Column("object_id", Integer, primary_key=True, autoincrement=True),
    Column("object_name", String(255), nullable=False),
    Column("object_subname", String(255)),
    Column("class_id", Integer, nullable=False),
    UniqueConstraint("object_name", "object_subname", "class_id", name="uq_objectname"),
    Index("ix_objectclass", "class_id"),
    ForeignKeyConstraint(["class_id"], ["invclasses.class_id"], name="fk_objectclass2", ondelete="CASCADE", onupdate="CASCADE"),
)

InventoryObjectAttributes = Table(
    "invobjectattributes",
    InventoryMetadata,
    Column("object_id", Integer, primary_key=True, autoincrement=False),
    Column("class_id", Integer, primary_key=True),
    Column("attr_key", String(255), primary_key=True),
    Column("attr_value", Text),
    Index("ix_attrKey", "attr_key"),
    ForeignKeyConstraint(["object_id", "class_id"], ["invobjects.object_id", "invobjects.class_id"], name="fk_objects", ondelete="CASCADE", onupdate="CASCADE"),
    ForeignKeyConstraint(["class_id", "attr_key"], ["invclassattributes.class_id", "invclassattributes.attr_key"], name="fk_invclassattributes", ondelete="CASCADE", onupdate="CASCADE"),
)


def CreateAllInventoryTables(sqlAlchemyEngine):
    InventoryMetadata.create_all(sqlAlchemyEngine)

    conn = sqlAlchemyEngine.connect()

    # Inserting Claasses
    conn.execute(InventoryClasses.insert().values({"class_namespace": "Indexes", "class_name": "Indexes"}))
    conn.execute(InventoryClasses.insert().values({"class_namespace": "Apps",    "class_name": "Apps"}))

    # Inserting ClassAttributes for Indexers
    result = conn.execute((InventoryClasses.select().where(InventoryClasses.c.class_namespace=="Indexes" and InventoryClasses.c.class_name=="Indexes"))).fetchone()
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "IndexOwner", "attr_name": "Splunk Index Owner", "attr_type": "string", "attr_mandatory": True}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "TargetedUsers", "attr_name": "Targeted Users", "attr_type": "string", "attr_mandatory": False}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "TargetedGroups", "attr_name": "Targeted Groups", "attr_type": "string", "attr_mandatory": False}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "Description", "attr_name": "Description", "attr_type": "string", "attr_mandatory": False}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "DataSensitive", "attr_name": "Data Sensitive", "attr_type": "bool", "attr_default": "False", "attr_mandatory": False}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "DailyQuotaGB", "attr_name": "Daily Quota in GB", "attr_type": "float", "attr_mandatory": True}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "RetentionDays", "attr_name": "Retention in Days", "attr_type": "int", "attr_mandatory": True}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "QuotaAlertMails", "attr_name": "Quota Alert Mails", "attr_type": "string", "attr_mandatory": False}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "CostCenter", "attr_name": "Cost Center", "attr_type": "string", "attr_mandatory": True}))

    # Inserting ClassAttributes for Apps
    result = conn.execute((InventoryClasses.select().where(InventoryClasses.c.class_namespace=="Apps" and InventoryClasses.c.class_name=="Apps"))).fetchone()
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "AppOwner", "attr_name": "Splunk App Owner", "attr_type": "string", "attr_mandatory": True}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "TargetedUsers", "attr_name": "Targeted Users", "attr_type": "string", "attr_mandatory": False}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "TargetedGroups", "attr_name": "Targeted Groups", "attr_type": "string", "attr_mandatory": False}))
    conn.execute(InventoryClassAttributes.insert().values({"class_id": result.class_id, "attr_key": "Description", "attr_name": "Description", "attr_type": "string", "attr_mandatory": False}))


