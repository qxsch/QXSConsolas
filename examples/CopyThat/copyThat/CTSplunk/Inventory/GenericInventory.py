import Metadata as md
import sqlalchemy.sql.expression as ex
from sqlalchemy.sql import and_, or_


class GenericInventory:
    _connection = None
    _transaction = None
    _attributes = {}
    _classId = None
    _objectName = None
    _objectSubName = None

    def __init__(self, sqlAlchemyConnection, namespace, class_name, objectName=None, objectSubName=None):
        self._connection = sqlAlchemyConnection
        self._namespace = namespace
        self._class_name = class_name
        self._loadAttributes()
        if objectName is None:
            objectName="object_name"
        if objectSubName is None:
            objectSubName="object_subname"
        self._objectName = objectName
        self._objectSubName = objectSubName

    def _loadAttributes(self):
        for row in self._connection.execute(ex.select([md.InventoryClasses.c.class_namespace, md.InventoryClasses.c.class_name, md.InventoryClassAttributes]).select_from(ex.join(md.InventoryClassAttributes, md.InventoryClasses, md.InventoryClassAttributes.c.class_id == md.InventoryClasses.c.class_id)).where(and_(md.InventoryClasses.c.class_namespace == self._namespace, md.InventoryClasses.c.class_name == self._class_name))):
            self._classId = row["class_id"]
            self._attributes[row["attr_key"]] = {}
            for i in ["attr_name", "attr_type", "attr_default", "attr_mandatory"]:
                self._attributes[row["attr_key"]][i] = row[i]

    def getAttributes(self):
        return self._attributes

    def list(self):
        return self.search()

    def search(self, object_name=None, object_subname=None, **kwargs):
        andList = [ md.InventoryObjects.c.class_id == self._classId ]
        orList = []
        if not object_name is None:
            andList.append(md.InventoryObjects.c.object_name.like(object_name))
        if not object_subname is None:
            andList.append(md.InventoryObjects.c.object_subname.like(object_subname))
        # append attributes subqueries
        for k in kwargs:
            if k in self._attributes:
                andList.append(md.InventoryObjects.c.object_id.in_(
                    ex.select([md.InventoryObjectAttributes.c.object_id]).select_from(md.InventoryObjectAttributes).where(and_(
                        md.InventoryObjectAttributes.c.class_id == self._classId,
                        md.InventoryObjectAttributes.c.attr_key == k,
                        md.InventoryObjectAttributes.c.attr_value.like(kwargs[k])
                    ))
                ))
        data = []
        for row in self._connection.execute(md.InventoryObjects.select().where(and_(*andList))):
            data.append({
                 "object_id": row["object_id"],
                 self._objectName : row["object_name"],
                 self._objectSubName : row["object_subname"]
            })
        return data

    def _lookupAttribtue(self, index):
        if isinstance(index, dict):
            if "object_id" in index:
                index["attributes"] = {}
                for row in self._connection.execute(md.InventoryObjectAttributes.select().where(and_(md.InventoryObjectAttributes.c.object_id == index["object_id"]))):
                    index["attributes"][row["attr_key"]] = row["attr_value"]
            return index
        else:
            d = {}
            for row in self._connection.execute(md.InventoryObjectAttributes.select().where(and_(md.InventoryObjectAttributes.c.object_id == index))):
                d[row["attr_key"]] = row["attr_value"]
            return d

    def lookupAttributes(self, index):
        if isinstance(index, list):
            newindex = []
            for i in index:
                newindex.append(self._lookupAttribtue(i))
            return newindex
        else:
            return self._lookupAttribtue(index)


class IndexInventory(GenericInventory):
    def __init__(self, sqlAlchemyConnection):
        GenericInventory.__init__(self, sqlAlchemyConnection, "Indexes", "Indexes", "indexName", "sourcetypeName")

    def search(self, indexName=None, sourcetypeName=None, **kwargs):
        return GenericInventory.search(self, object_name=indexName, object_subname=sourcetypeName, **kwargs)

class AppInventory(GenericInventory):
    def __init__(self, sqlAlchemyConnection):
        GenericInventory.__init__(self, sqlAlchemyConnection, "Apps", "Apps", "appName")

    def search(self, appName=None, **kwargs):
        return GenericInventory.search(self, object_name=appName, object_subname=None, **kwargs)


