import Metadata as md
import sqlalchemy.sql.expression as ex
from sqlalchemy.sql import and_, or_

class LookupException(Exception):
    pass
class EmptyLookupException(LookupException):
    pass

class GenericInventory(object):
    _connection = None
    _transaction = None
    _attributes = {}
    _classId = None
    _objectName = None
    _objectNameHR = None
    _objectSubName = None
    _objectSubNameHR = None

    def __init__(self, sqlAlchemyConnection, namespace, class_name, objectName=None, objectNameHR=None, objectSubName=None, objectSubNameHR=None):
        self._connection = sqlAlchemyConnection
        self._namespace = namespace
        self._class_name = class_name
        self._attributes = {}
        self._loadAttributes()
        if objectName is None:
            objectName="object_name"
        if objectNameHR is None:
            objectNameHR="Object Name"
        if objectSubName is None:
            objectSubName="object_subname"
        if objectSubNameHR is None:
            objectSubNameHR="Object Sub-Name"
        self._objectName = str(objectName)
        self._objectSubName = str(objectSubName)
        self._objectNameHR = str(objectNameHR)
        self._objectSubNameHR = str(objectSubNameHR)

    def getObjectNames(self):
        return [self._objectName, self._objectSubName]
    def getObjectNamesHR(self):
        return [self._objectNameHR, self._objectSubNameHR]

    def _loadAttributes(self):
        for row in self._connection.execute(ex.select([md.InventoryClasses.c.class_namespace, md.InventoryClasses.c.class_name, md.InventoryClassAttributes]).select_from(ex.join(md.InventoryClassAttributes, md.InventoryClasses, md.InventoryClassAttributes.c.class_id == md.InventoryClasses.c.class_id)).where(and_(md.InventoryClasses.c.class_namespace == self._namespace, md.InventoryClasses.c.class_name == self._class_name))):
            self._classId = row["class_id"]
            self._attributes[row["attr_key"]] = {}
            for i in ["attr_name", "attr_type", "attr_default", "attr_mandatory"]:
                self._attributes[row["attr_key"]][i] = row[i]

    def getAttributes(self):
        return self._attributes

    def getObjectById(self, object_id):
        if object_id is None:
            raise TypeError("object_id must be of type int")
        object_id = int(object_id)
        rows = self.search(object_id)
        if len(rows) == 1:
            return rows[0]
        if len(rows) == 0:
            raise EmptyLookupException("No objects were found for object_id " + str(object_id))
        raise LookupException("Too many objects were found for object_id " + str(object_id))

    def list(self):
        return self.search()

    def search(self, object_id=None, object_name=None, object_subname=None, **kwargs):
        andList = [ md.InventoryObjects.c.class_id == self._classId ]
        orList = []
        if not object_id is None:
            andList.append(md.InventoryObjects.c.object_id == object_id)
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
        self._attributes = {}
        #GenericInventory.__init__(self, sqlAlchemyConnection, "Indexes", "Indexes", "indexName", "Index", "sourcetypeName", "Sourcetype")
        super(IndexInventory, self).__init__(sqlAlchemyConnection, "Indexes", "Indexes", "indexName", "Index", "sourcetypeName", "Sourcetype")

    def search(self, object_id=None, indexName=None, sourcetypeName=None, **kwargs):
        #return GenericInventory.search(self, object_name=indexName, object_subname=sourcetypeName, **kwargs)
        return super(IndexInventory, self).search(object_id=object_id, object_name=indexName, object_subname=sourcetypeName, **kwargs)

class AppInventory(GenericInventory):
    def __init__(self, sqlAlchemyConnection):
        #GenericInventory.__init__(self, sqlAlchemyConnection, "Apps", "Apps", "appName", "App", "", "")
        super(AppInventory, self).__init__(sqlAlchemyConnection, "Apps", "Apps", "appName", "App", "", "")

    def search(self, object_id=None, appName=None, **kwargs):
        #return GenericInventory.search(self, object_name=appName, object_subname=None, **kwargs)
        return super(AppInventory, self).search(object_id=object_id, object_name=appName, object_subname=None, **kwargs)


