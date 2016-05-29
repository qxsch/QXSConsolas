import Metadata as md
import sqlalchemy.sql.expression as ex
from sqlalchemy import func
from sqlalchemy.sql import and_, or_

class LookupException(Exception):
    pass
class EmptyLookupException(LookupException):
    pass
class AttributeValidationException(Exception):
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

    def exists(self, object_id=None, object_name=None, object_subname=None):
        if object_id is None:
            try:
                if object_subname is None:
                    object_id = self.getObjectIdByName(object_name)
                else:
                    object_id = self.getObjectIdByName(object_name, object_subname)
                found = True
            except EmptyLookupException:
                found = False
        else:
            try:
                row = self._inventory.getObjectId(object_id)
                found = True
            except EmptyLookupException:
                found = False
        return found

    def getObjectIdByName(self, object_name, object_subname=None):
        andList = [ md.InventoryObjects.c.class_id == self._classId, md.InventoryObjects.c.object_name == object_name ]
        if not object_subname is None:
            andList.append(md.InventoryObjects.c.object_subname == object_subname)
        object_id = None
        i = 0
        for row in self._connection.execute(md.InventoryObjects.select().where(and_(*andList))):
            i = i + 1
            object_id = row["object_id"]
        if i > 1:
            raise LookupException("Too many objects were found")
        if i == 0:
            raise EmptyLookupException("No objects were found")
        return object_id

    def getObjectId(self, object_id):
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

    def delete(self, object_id=None, object_name=None, object_subname=None):
        assert not (object_id is None and object_name is None and object_subname is None), "At least one identifier must be set"
        if object_id is None:
            object_id = self.getObjectIdByName(object_name, object_subname)
        else:
            self.getObjectId(object_id)
        result = self._connection.execute(md.InventoryObjects.delete().where(and_(md.InventoryObjects.c.class_id == self._classId, md.InventoryObjects.c.object_id == object_id)))
        return result.rowcount

    def create(self, object_name, object_subname=None, **kwargs):
        assert not (object_name is None and object_subname is None), "At least one identifier must be set"
        self._validateAttributes(kwargs, checkMandatoryAttrs=True)
        valueList = { "class_id": self._classId, "object_name": object_name }
        if not object_subname is None:
            valueList["object_subname"] = object_subname
        # create the object
        result = self._connection.execute(md.InventoryObjects.insert().values(**valueList))
        new_object_id = result.inserted_primary_key
        if isinstance(new_object_id, list):
            new_object_id = new_object_id.pop()

        # update attributes
        self.updateAttributes(new_object_id, **kwargs)
        
        return new_object_id

    def removeAttributes(self, object_id=None, object_name=None, object_subname=None, attributeNames=[]):
        assert not (object_id is None and object_name is None and object_subname is None), "At least one identifier must be set"
        assert isinstance(attributeNames, list), "attributeNames must be of type list"
        if object_id is None:
            object_id = self.getObjectIdByName(object_name, object_subname)
        else:
            self.getObjectId(object_id)
        for k in attributeNames:
            if k not in self._attributes:
                raise AttributeValidationException("The attribute '" + k + "' does not exist.")
        for k in self._attributes:
            if (self._attributes[k]["attr_mandatory"]) and (k in attributeNames):
                raise AttributeValidationException("The attribute '" + k + "' is mandatory and cannot be removed.")
        for k in attributeNames:
            if self.attributeExists(object_id, k):
                 self._connection.execute(md.InventoryObjectAttributes.delete().where(and_(md.InventoryObjectAttributes.c.class_id == self._classId, md.InventoryObjectAttributes.c.object_id == object_id, md.InventoryObjectAttributes.c.attr_key == k)))

    def attributeExists(self, object_id, attribute_name):
        assert not (object_id is None), "At least one identifier must be set"
        for count in self._connection.execute(ex.select([func.count()]).select_from(md.InventoryObjectAttributes).where(and_(md.InventoryObjectAttributes.c.class_id == self._classId, md.InventoryObjectAttributes.c.object_id == object_id, md.InventoryObjectAttributes.c.attr_key == attribute_name))):
            count = count[0]
            if count == 0:
                return False
            else:
                return True

    def updateAttributes(self, object_id=None, object_name=None, object_subname=None, **kwargs):
        assert not (object_id is None and object_name is None and object_subname is None), "At least one identifier must be set"
        if object_id is None:
            object_id = self.getObjectIdByName(object_name, object_subname)
        else:
            self.getObjectId(object_id)
        self._validateAttributes(kwargs, checkMandatoryAttrs=False)
        for k in kwargs:
            if self.attributeExists(object_id, k):
                self._connection.execute(md.InventoryObjectAttributes.update().where(and_(md.InventoryObjectAttributes.c.class_id == self._classId, md.InventoryObjectAttributes.c.object_id == object_id, md.InventoryObjectAttributes.c.attr_key == k)).values(attr_value=str(kwargs[k])))
            else:
                self._connection.execute(md.InventoryObjectAttributes.insert().values(object_id=object_id, class_id=self._classId, attr_key=str(k), attr_value=str(kwargs[k])))

    def _validateAttributes(self, attributes, checkMandatoryAttrs=True):
        # check attributes
        for k in attributes:
            if k not in self._attributes:
                raise AttributeValidationException("The attribute '" + k + "' does not exist.")
            if attributes[k] is None:
                continue
            try:
                if self._attributes[k]["attr_type"] == "string":
                    attributes[k] = str(attributes[k])
                elif self._attributes[k]["attr_type"] == "bool":
                    attributes[k] = bool(attributes[k])
                elif self._attributes[k]["attr_type"] == "int":
                    attributes[k] = int(attributes[k])
                elif self._attributes[k]["attr_type"] == "float":
                    attributes[k] = float(attributes[k])
                elif self._attributes[k]["attr_type"] == "json":
                    attributes[k] = str(attributes[k])
            except:
                raise AttributeValidationException("The attribute '" + k + "' is not of type '" + self._attributes[k]["attr_type"] + "'")
        if checkMandatoryAttrs:
            for k in self._attributes:
                if (self._attributes[k]["attr_mandatory"]) and (k not in attributes):
                    raise AttributeValidationException("The attribute '" + k + "' is mandatory and has not been set")

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

    def getObjectIdByName(self, indexName, sourcetypeName):
        return super(IndexInventory, self).getObjectIdByName(object_name=indexName, object_subname=sourcetypeName)

    def search(self, object_id=None, indexName=None, sourcetypeName=None, **kwargs):
        return super(IndexInventory, self).search(object_id=object_id, object_name=indexName, object_subname=sourcetypeName, **kwargs)

    def delete(self, object_id=None, indexName=None, sourcetypeName=None):
        return super(IndexInventory, self).delete(object_id=object_id, object_name=indexName, object_subname=sourcetypeName)

    def create(self, indexName, sourcetypeName=None, **kwargs):
        return super(IndexInventory, self).create(object_name=indexName, object_subname=sourcetypeName, **kwargs)

    def removeAttributes(self, object_id=None, indexName=None, sourcetypeName=None, attributeNames=[]):
        return super(IndexInventory, self).removeAttributes(object_id=object_id, object_name=indexName, object_subname=sourcetypeName, attributeNames=attributeNames)

    def updateAttributes(self, object_id=None, indexName=None, sourcetypeName=None, **kwargs):
        return super(IndexInventory, self).updateAttributes(object_id=object_id, object_name=indexName, object_subname=sourcetypeName, **kwargs)



class AppInventory(GenericInventory):
    def __init__(self, sqlAlchemyConnection):
        #GenericInventory.__init__(self, sqlAlchemyConnection, "Apps", "Apps", "appName", "App", "", "")
        super(AppInventory, self).__init__(sqlAlchemyConnection, "Apps", "Apps", "appName", "App", "", "")

    def getObjectIdByName(self, appName):
        return super(IndexInventory, self).getObjectIdByName(object_name=appName, object_subname=None)

    def search(self, object_id=None, appName=None, **kwargs):
        #return GenericInventory.search(self, object_name=appName, object_subname=None, **kwargs)
        return super(AppInventory, self).search(object_id=object_id, object_name=appName, object_subname=None, **kwargs)

    def delete(self, object_id=None, appName=None):
        return super(IndexInventory, self).delete(object_id=object_id, object_name=appName, object_subname=None)

    def create(self, appName, **kwargs):
        return super(IndexInventory, self).create(object_name=appName, object_subname=None, **kwargs)

    def removeAttributes(self, object_id=None, appName=None, attributeNames=[]):
        return super(IndexInventory, self).removeAttributes(object_id=object_id, object_name=appName, object_subname=None, attributeNames=attributeNames)

    def updateAttributes(self, object_id=None, appName=None, **kwargs):
        return super(IndexInventory, self).updateAttributes(object_id=object_id, object_name=appName, object_subname=None, **kwargs)


