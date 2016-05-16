import logging, os
from QXSConsolas.Cli import CliApp
from QXSConsolas.Configuration import GetSystemConfiguration
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException
from Inventory import IndexInventory, AppInventory
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

def _GenerateOptions(name, opts, optionalOpts=[], prefix="attr-", ignoreMandatory=False):
    try:
        inv = GetInventory(name)
    except:
        return opts

    for k,v in inv.getAttributes().iteritems():
        if v["attr_default"] is None:
            if v["attr_mandatory"]:
                if ignoreMandatory:
                    opts.append({ "argument": "--" + prefix + k + "=",  "required": False, "description": v["attr_name"], "valuename": str(v["attr_type"]).upper() })
                else:
                    opts.append({ "argument": "--" + prefix + k + "=",  "required": bool(v["attr_mandatory"]), "description": v["attr_name"], "valuename": str(v["attr_type"]).upper() })
            else:
                optionalOpts.append({ "argument": "--" + prefix + k + "=",  "required": bool(v["attr_mandatory"]), "description": v["attr_name"], "valuename": str(v["attr_type"]).upper() })
        else:
            optionalOpts.append({ "argument": "--" + prefix + k + "=",  "default": v["attr_default"], "description": v["attr_name"], "valuename": str(v["attr_type"]).upper() })

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
        { "argument": "--index:",  "required": False, "description": "The name of the Index", "valuename": "INDEXNAME" },
        { "argument": "--sourcetype:", "required": False, "description": "The name of the SourceType", "valuename": "SOURCETYPENAME" },
    ], [], prefix="", ignoreMandatory=True)
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
        width = 0
        attrs = inv.getAttributes()
        for k,v in attrs.iteritems():
            width = max(width, len(v["attr_name"]))
        width = width + 1
        if width > 40:
            width = 40
        for entry in inv.lookupAttributes(inv.search(indexName=searchNames["--index:"], sourcetypeName=searchNames["--sourcetype:"], **searchAttrs)):
            puts(columns(["ID:", width], [colored.green(str(entry["object_id"])), None]))
            puts(columns(["Index:", width], [colored.green(str(entry["indexName"])), None]))
            puts(columns(["Sourcetype:", width], [colored.green(str(entry["sourcetypeName"])), None]))
            for k, v in entry["attributes"].iteritems():
                puts(columns([attrs[k]["attr_name"]+":", width], [str(v), None]))
            puts()

@CliApp(
    Name = "Search the Apps inventory",
    Description = "Search the Apps inventory",
#    Opts = []
    Opts = _GenerateOptions("Apps", [ 
        { "argument": "--app:",  "required": False, "description": "The name of the App", "valuename": "APP" },
    ], [], prefix="", ignoreMandatory=True)
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
        width = 0
        attrs = inv.getAttributes()
        for k,v in attrs.iteritems():
            width = max(width, len(v["attr_name"]))
        width = width + 1
        if width > 40:
            width = 40
        for entry in inv.lookupAttributes(inv.search(appName=searchNames["--app:"], **searchAttrs)):
            puts(columns(["ID:", width], [colored.green(str(entry["object_id"])), None]))
            puts(columns(["App:", width], [colored.green(str(entry["appName"])), None]))
            for k, v in entry["attributes"].iteritems():
                puts(columns([attrs[k]["attr_name"]+":", width], [str(v), None]))
            puts()


