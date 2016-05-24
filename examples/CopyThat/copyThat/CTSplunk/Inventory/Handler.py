from Inventory import GenericInventory
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
    _app = None

    def __init__(self, app, inventory):
        assert isinstance(inventory, GenericInventory), "Inventory is not a valid CTSplunk.Inventory.GenericInventory instance"
        self._inventory = inventory
        self._app = app


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


    def remove(self, object_id=None, object_name=None, object_subname=None):
        if object_id is None:
            object_name, object_subname = self.askForMissingObjectnames(object_name, object_subname)
        # TODO: remove object

    def updateWithPrompt(self, object_name=None, object_subname=None):
        object_name, object_subname = self.askForMissingObjectnames(object_name, object_subname)
        attrs = self.askForAllAttributes()
        self.update(object_name, object_subname, **attrs)

    def update(self, object_id=None, object_name=None, object_subname=None, **kwargs):
        if object_id is None:
            object_name, object_subname = self.askForMissingObjectnames(object_name, object_subname)
            if object_subname is None:
                rows = self._inventory.search(None, object_name)
            else:
                rows = self._inventory.search(None, object_name, object_subname)
        else:
            rows = self._inventory.search(object_id)
        if len(rows) == 0:
            # TODO: insert object
            pass
        elif len(rows) == 1:
            pass
        else:
            raise RuntimeError("Update failed: Too many objects to update")
        for k, v in kwargs.iteritems():
            if v is None:
                continue
            # TODO: update objectattribute
        # TODO: remove all attrs that are None

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



"""
# Standard non-empty input
name = prompt.query("What's your name?")

# Set validators to an empty list for an optional input
language = prompt.query("Your favorite tool (optional)?", validators=[])

# Shows a list of options to select from
inst_options = [{'selector':'1','prompt':'Full','return':'full'},
                {'selector':'2','prompt':'Partial','return':'partial'},
                {'selector':'3','prompt':'None','return':'no install'}]
inst = prompt.options("Full or Partial Install", inst_options)

# Use a default value and a validator
path = prompt.query('Installation Path', default='/usr/local/bin/', validators=[validators.PathValidator()])

puts(colored.blue('Hi {0}. Install {1} {2} to {3}'.format(name, inst, language or 'nothing', path)))
"""


