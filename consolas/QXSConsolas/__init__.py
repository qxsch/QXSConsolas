#!/usr/bin/python

import logging, logging.config
import sys, os, importlib
from QXSConsolas.Configuration import SysConf, Configuration
from QXSConsolas.Formatter import SimpleFormatter, ColoredFormatter
from QXSConsolas.Cli import Application

from clint.textui import puts, colored, indent
#__all__ = ('ColoredFormatter')



def run():
    """
    Runs QXSConsolas
    Configures the logger as well as the routing and runs the cli application
    """
    logging.config.dictConfig(SysConf().getValue("logging"))

    config = SysConf().getValue("routes.cliapps")
    if len(sys.argv) > 1 and sys.argv[1] in config and sys.argv[1] != "help":
        cmdname = sys.argv[1]
        modulename = ".".join(config[cmdname]["func"].split('.')[0:-1])
        classname = config[cmdname]["func"].split('.')[-1]
        # remove the first argument -> the module should not see this 
        sys.argv.pop(1)
        # run the app
        module = importlib.import_module(modulename)
        app = getattr(module, classname)
        app = app()
        assert isinstance(app, Application),  modulename + "." + classname + "() does not return a QXSConsolas.Cli.Application object"
        logger = None
        try:
            logger = logging.getLogger(config[cmdname]["logger"])
        except:
            pass
        data = None
        try:
            data = Configuration(configData = config[cmdname]["data"])
        except:
            pass
        return app.run(data = data, logger = logger)
    elif len(sys.argv) > 2 and sys.argv[2] in config and sys.argv[1] == "help":
        modulename = ".".join(config[sys.argv[2]]["func"].split('.')[0:-1])
        classname = config[sys.argv[2]]["func"].split('.')[-1]
        # run the app
        module = importlib.import_module(modulename)
        app = getattr(module, classname)
        app = app()
        assert isinstance(app, Application),  modulename + "." + classname + "() does not return a QXSConsolas.Cli.Application object" 
        # render it
        try:
            length = 0 
            for line in SysConf().getValue("routes.list.header").split("\n"):
                length = max(length, len(line))
            puts(colored.green("=" * length))
            puts(colored.green(SysConf().getValue("routes.list.header").rstrip()))
            puts(colored.green("=" * length) + "\n")
        except:
            pass
        puts("Command: " + colored.green(sys.argv[2]) + "\n")
        if "description" in config[sys.argv[2]]:
            with indent(4):
                puts(config[sys.argv[2]]["description"] + "\n")

        showCliName = True
        showCliDescription = True
        if "showCliName" in config[sys.argv[2]]:
            showCliName = bool(config[sys.argv[2]]["showCliName"])
        if "showCliDescription" in config[sys.argv[2]]:
            showCliDescription = bool(config[sys.argv[2]]["showCliDescription"])

        with indent(4):
            #app.showHelp(False, False)
            app.showHelp(showCliName, showCliDescription)
        try:
            puts("\n" + SysConf().getValue("routes.list.footer").rstrip() + "\n")
        except:
            pass
    else:
        try:
            length = 0 
            for line in SysConf().getValue("routes.list.header").split("\n"):
                length = max(length, len(line))
            puts(colored.green("=" * length))
            puts(colored.green(SysConf().getValue("routes.list.header").rstrip()))
            puts(colored.green("=" * length) + "\n")
        except:
            pass
        try:
            puts(SysConf().getValue("routes.list.description").rstrip() + "\n")
        except:
            pass
        puts("Available commands:")
        for routename in config:
            if routename == "help":
                continue
            with indent(2):
                if "func" in config[routename]:
                    puts(colored.green(routename))
                    if "description" in config[routename]:
                        with indent(4):
                            puts(config[routename]["description"])
        with indent(2):
            puts(colored.green("help") + " [" + colored.yellow("command") + "]")
            with indent(4):
                puts("Show the help [for a command]")
        try:
            puts("\n" + SysConf().getValue("routes.list.footer").rstrip() + "\n")
        except:
            pass
    return 1

