from Inventory import GenericInventory
from clint.textui import puts, columns, colored, prompt, validators


class ConsoleHandler(object):
    _inventory = None
    _app = None

    def __init__(self, app, inventory):
        assert isinstance(inventory, GenericInventory), "Inventory is not a valid CTSplunk.Inventory.GenericInventory instance"
        self._inventory = inventory
        self._app = app


    def _getObjectNames(self):
        objectnamePrompt, objectsubnamePrompt  = self._inventory.getObjectNames()
        objectnamePromptHR, objectsubnamePromptHR  = self._inventory.getObjectNamesHR()
        objectnamePromptHR = str(objectnamePromptHR)
        objectsubnamePromptHR = str(objectsubnamePromptHR)
        objectnamePrompt = str(objectnamePrompt)
        objectsubnamePrompt = str(objectsubnamePrompt)
        return [objectnamePrompt, objectnamePromptHR, objectsubnamePrompt, objectsubnamePromptHR ]

    def _askForMissingObjectnames(self, object_name, object_subname):
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

    def _askForAllAttributes(self, attrs, skipKeys=[]):
        attributes = {}
        for k, v in self._inventory.getAttributes().iteritems():
            if k in attrs:
                attributes[k] = attrs[k]
            elif k not in skipKeys:
                attributes[k] = prompt.query(v["attr_name"] + ":", validators=[])
        return attributes

    def remove(self, object_id=None, object_name=None, object_subname=None):
        if object_id is None:
            object_name, object_subname = self._askForMissingObjectnames(object_name, object_subname)

    def update(self, object_id=None, object_name=None, object_subname=None, **kwargs):
        if object_id is None:
            object_name, object_subname = self._askForMissingObjectnames(object_name, object_subname)
            if object_subname is None:
                rows = self._inventory.search(None, object_name)
            else:
                rows = self._inventory.search(None, object_name, object_subname)
        else:
            rows = self._inventory.search(object_id)
        if len(rows) == 0:
            # insert
            pass
        elif len(rows) == 1:
            # update
            pass
        else:
            raise RuntimeError("Update failed: Too many objects to update")

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
        pass



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


