from Inventory import GenericInventory, EmptyLookupException
from clint.textui import puts, columns, colored, prompt, validators
import re


class IntegerValidator(object):
    message = 'Enter a valid number.'
    _emptyValues = False

    def __init__(self, message=None, allowEmptyValues=False):
        if message is not None:
            self.message = message
        self._emptyValues = bool(allowEmptyValues)

    def __call__(self, value):
        """
        Validates that the input is a integer.
        """
        try:
            if value == "" and self._emptyValues:
                return value
            return int(value)
        except (TypeError, ValueError):
            raise validators.ValidationError(self.message)

class FloatValidator(object):
    message = 'Enter a valid float.'
    _emptyValues = False

    def __init__(self, message=None, allowEmptyValues=False):
        if message is not None:
            self.message = message
        self._emptyValues = bool(allowEmptyValues)

    def __call__(self, value):
        """
        Validates that the input is a integer.
        """
        try:
            if value == "" and self._emptyValues:
                return value
            return float(value)
        except (TypeError, ValueError):
            raise validators.ValidationError(self.message)



class ConsoleHandler(object):
    _inventory = None
    _logger = None

    def __init__(self, inventory, logger=None):
        assert isinstance(inventory, GenericInventory), "Inventory is not a valid CTSplunk.Inventory.GenericInventory instance"
        self._inventory = inventory
        self._logger = logger


    def _getObjectNames(self):
        objectnamePrompt, objectsubnamePrompt = self._inventory.getObjectNames()
        objectnamePromptHR, objectsubnamePromptHR = self._inventory.getObjectNamesHR()
        objectnamePromptHR = str(objectnamePromptHR)
        objectsubnamePromptHR = str(objectsubnamePromptHR)
        objectnamePrompt = str(objectnamePrompt)
        objectsubnamePrompt = str(objectsubnamePrompt)
        return [objectnamePrompt, objectnamePromptHR, objectsubnamePrompt, objectsubnamePromptHR ]

    def askForMissingObjectnames(self, object_name, object_subname):
        objectnamePrompt, objectnamePromptHR, objectsubnamePrompt, objectsubnamePromptHR = self._getObjectNames()
        if objectnamePromptHR == "":
            objectnamePromptHR = objectnamePrompt
        if objectsubnamePromptHR == "":
            objectsubnamePromptHR = objectsubnamePrompt
        if object_name is None:
            object_name = prompt.query(objectnamePromptHR + ":")
        if object_subname is None:
            if objectsubnamePrompt != "":
                object_subname = prompt.query(objectsubnamePromptHR + ":")
        return [object_name, object_subname]

    def _prompt(self, attrName, attrDef):
	attrDef["attr_type"] = str(attrDef["attr_type"]).lower()
        v = []
        if attrDef["attr_type"] == "string":
            if attrDef["attr_mandatory"]:
                v.append(validators.RegexValidator(r'.+', 'Enter a value, that is not empty.'))
            result = prompt.query(attrDef["attr_name"] + ":", validators=v)
            if result == "" or result is None:
                return None
            return str(result)
        elif attrDef["attr_type"] == "bool":
            if attrDef["attr_mandatory"]:
                v.append(validators.RegexValidator(re.compile('^(true|false|0|1)$', re.IGNORECASE), 'Enter true, 1, false or 0.'))
            else:
                v.append(validators.RegexValidator(re.compile('^(true|false|0|1)?$', re.IGNORECASE), 'Enter true, 1, false or 0.'))
            result = prompt.query(attrDef["attr_name"] + ":", validators=v)
            if result == "" or result is None:
                return None
            return bool(result)
        elif attrDef["attr_type"] == "int":
            v.append(IntegerValidator('Enter a valid integer.', not attrDef["attr_mandatory"]))
            result = prompt.query(attrDef["attr_name"] + ":", validators=v)
            if result == "" or result is None:
                return None
            return int(result)
        elif attrDef["attr_type"] == "float":
            v.append(FloatValidator('Enter a valid float.', not attrDef["attr_mandatory"]))
            result = prompt.query(attrDef["attr_name"] + ":", validators=v)
            if result == "" or result is None:
                return None
            return float(result)
        elif attrDef["attr_type"] == "json":
            # todo add json validation
            if attrDef["attr_mandatory"]:
                v.append(validators.RegexValidator(r'.+'))
            return prompt.query(attrDef["attr_name"] + ":", validators=v)
        return None

    def askForAllAttributes(self, predefinedAttrs={}, skipKeys=[]):
        attributes = {}
        for k, v in self._inventory.getAttributes().iteritems():
            if k in predefinedAttrs:
                attributes[k] = predefinedAttrs[k]
            elif k not in skipKeys:
                attributes[k] = self._prompt(k, v)
        return attributes

    def askForRequiredAttributes(self, predefinedAttrs={}):
        skipKeys = []
        for k, v in self._inventory.getAttributes().iteritems():
            if not v["attr_mandatory"]:
                skipKeys.append(k)
        return self.askForAllAttributes(predefinedAttrs, skipKeys)


    def delete(self, object_id=None, object_name=None, object_subname=None):
        if object_id is None:
            object_name, object_subname = self.askForMissingObjectnames(object_name, object_subname)
            if object_subname is None:
                c = self._inventory.delete(None, object_name)
            else:
                c = self._inventory.delete(None, object_name, object_subname)
        else:
            c = self._inventory.delete(object_id)
        puts(colored.yellow(str(c) + " entries deleted."))

    def exists(self, object_id=None, object_name=None, object_subname=None):
        if object_id is None:
            if object_subname is None:
                return self._inventory.exists(None, object_name)
            else:
                return self._inventory.exists(None, object_name, object_subname)
        else:
            return self._inventory.exists(object_id)

    def updateWithPrompt(self, object_name=None, object_subname=None, updateAll=True):
        object_name, object_subname = self.askForMissingObjectnames(object_name, object_subname)
        if updateAll:
            attrs = self.askForAllAttributes()
        else:
            attrs = self.askForRequiredAttributes()
        return self.update(None, object_name, object_subname, **attrs)

    def update(self, object_id=None, object_name=None, object_subname=None, **kwargs):
        if object_id is None:
            object_name, object_subname = self.askForMissingObjectnames(object_name, object_subname)
            insert = True
            try:
                if object_subname is None:
                    object_id = self._inventory.getObjectIdByName(object_name)
                else:
                    object_id = self._inventory.getObjectIdByName(object_name, object_subname)
                insert = False
            except EmptyLookupException:
                insert = True
        else:
            insert = True
            try:
                row = self._inventory.getObjectId(object_id)
                insert = False
            except EmptyLookupException:
                insert = True

        if insert:
            # create
            attrs = {}
            for k, v in self.askForRequiredAttributes(kwargs).iteritems():
                if not(v is None):
                    attrs[k]=v

            if object_subname is None:
                return self._inventory.create(object_name, **attrs)
            else:
                return self._inventory.create(object_name, object_subname, **attrs)
        else:
            attrs = {}
            delAttrs = []
            attrDef = self._inventory.getAttributes()
            for k,v in kwargs.iteritems():
                if v is None:
                    if not attrDef[k]["attr_mandatory"]:
                        delAttrs.append(k)
                else:
                    attrs[k]=v
            self._inventory.updateAttributes(object_id, **attrs)
            self._inventory.removeAttributes(object_id, attributeNames=delAttrs)

        return object_id

    def display(self, entries):
        objectnamePrompt, objectnamePromptHR, objectsubnamePrompt, objectsubnamePromptHR = self._getObjectNames()
        width = 0
        attrs = self._inventory.getAttributes()
        for k,v in attrs.iteritems():
            width = max(width, len(v["attr_name"]))
        width = width + 1
        if width > 40:
            width = 40
        c = 0
        for entry in self._inventory.lookupAttributes(entries):
            c = c + 1
            puts(columns(["ID:", width], [colored.green(str(entry["object_id"])), None]))
            puts(columns([objectnamePromptHR, width], [colored.green(str(entry[objectnamePrompt])), None]))
            if objectsubnamePrompt:
                puts(columns([objectsubnamePromptHR, width], [colored.green(str(entry[objectsubnamePrompt])), None]))
            for k, v in entry["attributes"].iteritems():
                puts(columns([attrs[k]["attr_name"]+":", width], [str(v), None]))
            puts()

        puts(colored.yellow(str(c) + " entries found."))


