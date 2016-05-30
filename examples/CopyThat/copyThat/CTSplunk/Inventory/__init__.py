import logging, os
from QXSConsolas.Cli import CliApp
from QXSConsolas.Configuration import GetSystemConfiguration
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException
from Inventory import IndexInventory, AppInventory
from Handler import ConsoleHandler
from sqlalchemy import create_engine
from clint.textui import puts, columns, colored, prompt, validators

class NoInventoryEngine(Exception):
    pass

def GetInventoryEngine():
    if GetInventoryEngine._engine is None:
        raise NoInventoryEngine("SplunkInventory.datasource is invalid or not defined in the configuration.")
    return GetInventoryEngine._engine

def GetInventory(name):
    if name in GetInventory._inventories:
        return GetInventory._inventories[name]
    if not GetInventory._inventories:
        raise NoInventoryEngine("SplunkInventory.datasource is invalid or not defined in the configuration.")
    raise KeyError("Inventory '" + name + "' does not exist.")

# initialize the engine
try:
    GetInventory._inventories = {}
    GetInventoryEngine._engine = None
    GetInventoryEngine._engine = create_engine(GetSystemConfiguration().get("SplunkInventory.datasource"))

    GetInventory._inventories["Indexes"] = IndexInventory(GetInventoryEngine())
    GetInventory._inventories["Apps"] = AppInventory(GetInventoryEngine())
except:
    pass


def _GenerateOptions(name, opts, optionalOpts=[], prefix="attr-", ignoreMandatory=False, setDefaultValues=True, prefixDescription=""):
    try:
        inv = GetInventory(name)
    except:
        return opts

    for k,v in inv.getAttributes().iteritems():
        if v["attr_default"] is None:
            if v["attr_mandatory"]:
                if ignoreMandatory:
                    opts.append({ "argument": "--" + prefix + k + "=",  "required": False, "description": prefixDescription + v["attr_name"], "valuename": str(v["attr_type"]).upper() })
                else:
                    opts.append({ "argument": "--" + prefix + k + "=",  "required": bool(v["attr_mandatory"]), "description": prefixDescription + v["attr_name"], "valuename": str(v["attr_type"]).upper() })
            else:
                optionalOpts.append({ "argument": "--" + prefix + k + "=",  "required": bool(v["attr_mandatory"]), "description": prefixDescription + v["attr_name"], "valuename": str(v["attr_type"]).upper() })
        else:
            if setDefaultValues:
                optionalOpts.append({ "argument": "--" + prefix + k + "=",  "default": v["attr_default"], "description": prefixDescription + v["attr_name"], "valuename": str(v["attr_type"]).upper() })
            else:
                if v["attr_mandatory"] and not ignoreMandatory:
                    opts.append({ "argument": "--" + prefix + k + "=",  "required": bool(v["attr_mandatory"]), "description": prefixDescription + v["attr_name"], "valuename": str(v["attr_type"]).upper() })
                else:
                    optionalOpts.append({ "argument": "--" + prefix + k + "=", "description": prefixDescription + v["attr_name"], "valuename": str(v["attr_type"]).upper() })

    opts.extend(optionalOpts)
    return opts

def _GetAttrOptions(name, opts, prefix="attr-"):
    d = {}
    inv = GetInventory(name)
    for k,v in inv.getAttributes().iteritems():
        if "--" + prefix + k + "=" in opts:
            d[k] = opts["--" + prefix + k + "="]
    return d

@CliApp(
    Name = "Search the Indexes inventory",
    Description = "Search the Indexes inventory",
    Opts = _GenerateOptions("Indexes", [ 
        { "argument": "--index:",  "required": False, "description": "Search by the name of the Index", "valuename": "INDEXNAME" },
        { "argument": "--sourcetype:", "required": False, "description": "Search by the name of the SourceType", "valuename": "SOURCETYPENAME" },
    ], [], prefix="", prefixDescription="Search by ", ignoreMandatory=True, setDefaultValues=False)
)
def SearchIndex(app):
    searchNames = {}
    for k in ["--index:", "--sourcetype:" ]:
        searchNames[k] = None
        if k in app.options:
            searchNames[k] = app.options[k]
    searchAttrs = _GetAttrOptions("Indexes", app.options, prefix="")
    with GetInventoryEngine().begin() as conn:
        inv = IndexInventory(conn)
        h = ConsoleHandler(inv, app.logger)
        h.display(inv.search(indexName=searchNames["--index:"], sourcetypeName=searchNames["--sourcetype:"], **searchAttrs))

@CliApp(
    Name = "Create an App in the Apps inventory",
    Description = "Create an App in the Apps inventory",
    Opts = _GenerateOptions("Indexes", [ 
        { "argument": "--index:",  "required": True, "description": "Set the name of the Index", "valuename": "INDEXNAME" },
        { "argument": "--sourcetype:", "required": True, "description": "Set the name of the SourceType", "valuename": "SOURCETYPENAME" },
    ], [], prefix="", prefixDescription="Set a value for ", ignoreMandatory=True, setDefaultValues=True)
)
def CreateIndex(app):
    searchNames = {}
    for k in ["--app:"]:
        searchNames[k] = None
        if k in app.options:
            searchNames[k] = app.options[k]
    searchAttrs = _GetAttrOptions("Apps", app.options, prefix="")
    with GetInventoryEngine().begin() as conn:
        inv = IndexInventory(conn)
        h = ConsoleHandler(inv, app.logger)
        h.update(searchNames["--app:"], None, **searchAttrs)


@CliApp(
    Name = "Search the Apps inventory",
    Description = "Search the Apps inventory",
    Opts = _GenerateOptions("Apps", [ 
        { "argument": "--app:",  "required": False, "description": "Search by the name of the App", "valuename": "APP" },
    ], [], prefix="", prefixDescription="Search by ", ignoreMandatory=True, setDefaultValues=True)
)
def SearchApp(app):
    searchNames = {}
    for k in ["--app:"]:
        searchNames[k] = None
        if k in app.options:
            searchNames[k] = app.options[k]
    searchAttrs = _GetAttrOptions("Apps", app.options, prefix="")
    with GetInventoryEngine().begin() as conn:
        inv = AppInventory(conn)
        h = ConsoleHandler(inv, app.logger)
        h.display(inv.search(appName=searchNames["--app:"], **searchAttrs))

@CliApp(
    Name = "Create the Apps inventory",
    Description = "Create the Apps inventory",
    Opts = _GenerateOptions("Apps", [ 
        { "argument": "--app:",  "required": True, "description": "Set the name of the App", "valuename": "APP" },
    ], [], prefix="", prefixDescription="Set a value for ", ignoreMandatory=False, setDefaultValues=False)
)
def CreateApp(app):
    searchNames = {}
    for k in ["--app:"]:
        searchNames[k] = None
        if k in app.options:
            searchNames[k] = app.options[k]
    searchAttrs = _GetAttrOptions("Apps", app.options, prefix="")
    with GetInventoryEngine().begin() as conn:
        inv = AppInventory(conn)
        h = ConsoleHandler(inv, app.logger)
        h.update(searchNames["--app:"], None, **searchAttrs)


