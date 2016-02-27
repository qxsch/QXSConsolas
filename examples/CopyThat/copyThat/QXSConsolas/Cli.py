#!/usr/bin/python

import os, sys, inspect, re, logging
from QXSConsolas.Configuration import Configuration, SysConf
from clint.textui import puts, colored, indent
from functools import wraps

class ApplicationException(Exception):
    pass
class ArgumentParserException(Exception):
    pass

class ArgumentParser:
    """
    Parses cli arguments and options from the sys.argv or another list
    """
    _opts = {}

    options = {}
    arguments = []

    def __init__(self, opts = []):
        """
        Creates the argument parser
        opts is a list of dicts, that will be passed to the addOptionDefinition method
        """
        assert isinstance(opts, list), "longopts must be a list"
        for lopt in opts:
            assert isinstance(lopt, dict), "every element in longopts must be a dict"
            self.addOptionDefinition(**lopt)

    def getOptionDefinitions(self):
        """
        Returns a dict of the current option definitions
        """
        return self._opts
        
    def getCollapsedOptionDefinitions(self):
        """
        Returns a dict of the current option definitions with references collapsed in their final parent
        """
        definitions = {}
        for key in self._opts:
            finalKey=self._resolveFinalKey(key)
            if not finalKey in definitions:
                definitions[finalKey] = { "referencedBy": [] }
            if key == finalKey:
                for subKey in ["description", "default", "required", "multiple", "references", "valuename"]:
                    definitions[finalKey][subKey] = self._opts[finalKey][subKey]
            else:
                definitions[finalKey]["referencedBy"].append(key)
                
        return definitions

    def clearOptionDefinitions(self):
        """
        Clears the current option definitions
        """
        self._longopts = {}

    def addOptionDefinition(
        self, 
        argument,
        description = "",
        default = None,
        required = False,
        multiple = False,
        references = None,
        valuename = "VALUE"
    ):
        """
        Adds a new definition to the option definitions
        """
        if not references is None:
            if not references in self._opts:
                raise ArgumentParserException("You cannot specify a reference \"" + references + "\" that does not exist for argument \"" + argument + "\"")
        self._opts[argument] = {
            "description": str(description),
            "default": default,
            "required": bool(required),
            "multiple": bool(multiple),
            "references": references,
            "valuename": str(valuename)
        }

    def _resolveFinalKey(self, key):
        """
        Resolves the final key for a key in case it references another option definition
        """
        # final key resolution
        i = 0
        tmpopt = self._opts[key]
        while "references" in tmpopt and tmpopt["references"] in self._opts:
            key = tmpopt["references"]
            tmpopt = self._opts[key]
            i = i + 1
            if i > 40:
                raise ArgumentParserException("Infinite argument reference detected.")
        return key

    def _setOption(self, key, value, opt):
        """
        This adds a value to the options property
        """
        key = str(key)
        if value is None:
            value = opt["default"]

        # final key resolution
        key = self._resolveFinalKey(key)

        if key in self.options:
            if opt["multiple"]:
                self.options[key].append(value)
            else:
                raise ArgumentParserException("The option \"" + key + "\" cannot be declared multiple times.")
        else:
            if opt["multiple"]:
                self.options[key] = [ value ]
            else:
                self.options[key] = value

    def parseArguments(self, argv=None):
        """
        Parses the argument with argv as a list
        In case argv is None sys.argv will be used
        Returns (options, arguments)
        Also sets the options and arguments properties
        """
        self.options = {}
        self.arguments = []
        # None? use sys.argv
        if argv is None:
            argv = sys.argv[1:]

        reOpt = re.compile('^(-[a-zA-Z]{1,3}|--[^ \t\n\r=]+)$')
        reOptEquals = re.compile('^(--[^ \t\n\r=]+=)(.*)$')
        lastKey = None
        lastKeyOptDef = None
        lastKeyIsOptional = True
        for arg in argv:
            if not lastKey is None:
                if lastKeyIsOptional:
                    if arg[0] != "-":
                        self._setOption(lastKey, arg, lastKeyOptDef)
                        lastKey = None
                        continue
                    else:
                        self._setOption(lastKey, None, lastKeyOptDef)
                        lastKey = None
                else:
                   self._setOption(lastKey, arg, lastKeyOptDef)
                   lastKey = None
                   continue
            # long with equals match?
            m = reOptEquals.match(arg)
            if not m is None:
                if m.group(1) in self._opts:
                    self._setOption(m.group(1), m.group(2), self._opts[m.group(1)])
                    continue
                else:
                    self.arguments.append(arg)
                    continue
            # short / long match?
            m = reOpt.match(arg)
            if not m is None:
                if m.group(1) in self._opts:
                    self._setOption(m.group(1), None, self._opts[m.group(1)])
                elif m.group(1) + ":" in self._opts:
                    lastKey = m.group(1) + ":"
                    lastKeyIsOptional = False
                    lastKeyOptDef =  self._opts[lastKey]
                    continue
                elif m.group(1) + "::" in self._opts:
                    lastKey = m.group(1) + "::"
                    lastKeyIsOptional = True
                    lastKeyOptDef =  self._opts[lastKey]
                    continue
                else:
                    self.arguments.append(arg)
                    continue
            self.arguments.append(arg)
        # check if we hav a lastKey entry
        if not lastKey is None:
            if lastKeyIsOptional:
               self._setOption(lastKey, None, lastKeyOptDef)
            else:
               raise ArgumentParserException("The option \"" + lastKey + "\" requires a value.")
        # check all required arguments
        for key in self._opts:
            key = self._resolveFinalKey(key)
            if self._opts[key]["required"]:
                if not key in self.options:
                    raise ArgumentParserException("The option \"" + key + "\" is required!")
        return (self.options, self.arguments)



class Application:
    """
    This is the cli application
    The QXSConsolas.run() method works with Application objects.
    The Application Object will also be passed to the cli function that will be decorated
    """

    _app = None
    _argparser = None

    name = None
    description = None
    data = None
    configuration = None
    logger = None
    options = None
    arguments = None

    def __init__(
        self,
        app = None,
        opts = [],
        data = None,
        logger = None,
        configuration = None,
        name = None,
        description = None
    ):
        """
        Creates the application
        app is the function, that will be called
        opts are the options for the ArgumentParser object
        logger is a logger object
        data is application specific data (as a configuration object)
        configuration is the system configuration (as configuration object)
        name is the name of the cli endpoint
        description is the description of the cli endpoint
        """
        self._app = app
        self._argparser = ArgumentParser(opts = opts)
        assert logger is None or isinstance(logger, logging.Logger), "logger is not a valid logging.Logger"
        if self.logger is None:
            self.logger = logging
        else:
            self.logger = logger
        assert data is None or isinstance(data, Configuration), "data is not a valid QXSConsolas.Configuration.Configuration"
        self.data = data
        if configuration is None:
            self.configuration = SysConf()
        else:
            assert isinstance(configuration, Configuration), "data is not a valid QXSConsolas.Configuration.Configuration"
            self.configuration = configuration
        if name is None:
            self.name = ""
        else:
            self.name = str(name)
        if description is None:
            self.description = ""
        else:
            self.description = str(description)

    def getHelpDict(self):
        """
        Returns the help of the application
        """
        return self._argparser.getCollapsedOptionDefinitions()


    def formatArgumentName(self, argumentName, valueName="VALUE"):
        """
        Formats an argument name
        """
        argumentName = str(argumentName).split('=')
        if len(argumentName) > 1:
           return colored.green(argumentName[0] + "=") + colored.yellow(str(valueName))
        argumentName = str(argumentName[0]).split(':')
        if len(argumentName) >= 3:
           return colored.green(argumentName[0]) + " [" + colored.yellow(str(valueName)) + "]"
        if len(argumentName) >= 2:
           return colored.green(argumentName[0]) + " " + colored.yellow(str(valueName))
        return colored.green(argumentName[0])

    def formatArgumentDefinitionBlock(self, argumentName, defBlock):
        """
        Formats a definition block
        """
        s = self.formatArgumentName(argumentName, defBlock["valuename"])
        for arg in defBlock["referencedBy"]:
           s += ", " + self.formatArgumentName(arg, defBlock["valuename"])
        
        if not defBlock["default"] is None:
            s += "   (Default: " + str(defBlock["default"]) + ")"

        if defBlock["multiple"]:
            s += "   (" + colored.cyan("Multiple times allowed") + ")"

        if defBlock["required"]:
            s += "   (" + colored.red("Required") + ")"

        if str(defBlock["description"]) != "":
            s += "\n    "
            s += "\n    ".join(str(defBlock["description"]).split("\n"))
        s += "\n"

        return s

    def showHelp(self, showName = True, showDescription = True):
        """
        Prints the the help of the application
        """
        definition = self._argparser.getCollapsedOptionDefinitions()
        if showName and not self.name is None and self.name != "":
            length = 0 
            for line in self.name.split("\n"):
                length = max(length, len(line))
            puts(colored.green("=" * length))
            puts(colored.green(self.name.rstrip()))
            puts(colored.green("=" * length) + "\n")
        if showDescription and not self.description is None and self.description != "":
            puts(self.description + "\n")
        for key in definition:
            puts(self.formatArgumentDefinitionBlock(key, definition[key]))

    def run(self, argv = None, data = None, logger = None):
        """
        Runs the function
        """
        if not logger is None:
            assert isinstance(logger, logging.Logger), "logger is not a valid logging.Logger"
            self.logger = logger
        if not data is None:
            assert isinstance(data, Configuration), "data is not a valid QXSConsolas.Configuration.Configuration"
            self.data = data

        self.options, self.arguments = self._argparser.parseArguments(argv)
        self._app(ApplicationData(self))


class ApplicationData:
    name = None
    description = None
    data = None
    configuration = None
    logger = None
    options = dict()
    arguments = list()

    def __init__(
        self,
        app
    ):
        """
        Creates the application data
        app the Application object
        """
        assert isinstance(app, Application), "An application object is required!"
        self.data = app.data
        self.logger = app.logger
        self.configuration = app.configuration
        self.options = app.options
        self.arguments = app.arguments
        self.name = app.name
        self.description = app.description

    def log(self, message, level="info"):
        if hasattr(self.logger, level):
            l = getattr(self.logger, level)
            l(message)
        else:
            self.loggger.info(message)


def CliApp(
    Name = None,
    Description = None,
    Opts = []
):
    """
    Decorator for a function, that returns a cli application

    Name is the name of the application
    Description is the description of the application
    Opts is a list of dict
        Each dict must contain the following options:
            arguemnt  is a string in the following form:
                "--name"   is a long  option without a value
                "-z"       is a short option without a value
                "--name:"  is a long  option with a required value
                "-z:"      is a short option with a required value
                "--name::" is a long  option with an optional value
                "-z::"     is a short option with an optional value
                "--name="  is a long  option with value after the "=" char
        Each dict can contain the following options:
            description is a string, that describes the argument
            default     is a default value, that will be used in case a value is absent
            required    is a bool, in case of True, the argument is required
            multiple    is a bool, in case of True, the argument can be used multiple times
            references  is a string, that holds the reference to another argument dict definition
            valuename   is a string, that will be shown in the help as the VALUE placeholder
       
    """
    assert isinstance(Opts, list), "Opts must be a list"
    for lopt in Opts:
        assert isinstance(lopt, dict), "every element in Opts must be a dict"
    def CliAppDecorator(func):
        @wraps(func)
        def FuncWrapper():
            return Application(app = func, opts = Opts, name = Name, description = Description)
        return FuncWrapper
    return CliAppDecorator


