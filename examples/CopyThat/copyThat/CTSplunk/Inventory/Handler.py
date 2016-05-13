from Inventory import GenericInventory
from clint.textui import puts, columns, colored, prompt, validators


class ConsoleHandler:
    _inventory = None

    def __init__(self, inventory):
        assert isinstance(inventory, GenericInventory), "Inventory is not a valid CTSplunk.Inventory.GenericInventory instance"
        self._inventory = inventory

    def _askForMissingObjectnames(self, object_name, object_subname):
        objectnamePrompt, objectsubnamePrompt  = self._inventory.getObjectNames()
        objectnamePromptHR, objectsubnamePromptHR  = self._inventory.getObjectNamesHR()
        objectnamePromptHR = str(objectnamePromptHR)
        objectsubnamePromptHR = str(objectsubnamePromptHR)
        objectnamePrompt = str(objectnamePrompt)
        objectsubnamePrompt = str(objectsubnamePrompt)

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

    def _askForAllAttributes(self, kwargs, skipKeys=[]):
        for k, v in self._inventory.getAttributes().iteritems():
            if k not in skipKeys:
                prompt.query(v["attr_name"] + ":", validators=[])
                print(str(k) + " = " + str(v))

    def add(self, object_name=None, object_subname=None, **kwargs):
        object_name, object_subname = self._askForMissingObjectnames(object_name, object_subname)
        attributes = self._askForAllAttributes(kwargs)

    def remove(self, object_id=None, object_name=None, object_subname=None):
        if object_id is None:
            object_name, object_subname = self._askForMissingObjectnames(object_name, object_subname)

    def update(self, object_id=None, object_name=None, object_subname=None, **kwargs):
        if object_id is None:
            object_name, object_subname = self._askForMissingObjectnames(object_name, object_subname)


    def list(self):
        pass

    def search(self, object_name=None, object_subname=None, **kwargs):
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


