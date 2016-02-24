#!/usr/bin/python

import os, sys, inspect, re, logging
import QXSConsolas.Configuration
from clint.textui import puts, colored, indent
from functools import wraps

class ApplicationException(Exception):
    pass
class ArgumentParserException(Exception):
    pass

class ArgumentParser:
    _opts = {}

    options = {}
    arguments = []

    def __init__(self, opts = []):
        assert isinstance(opts, list), "longopts must be a list"
        for lopt in opts:
            assert isinstance(lopt, dict), "every element in longopts must be a dict"
            self.addOptionDefinition(**lopt)

    def getOptionDefinitions(self):
        return self._opts
        
    def getCollapsedOptionDefinitions(self):
        definitions = {}
        for key in self._opts:
            finalKey=self.resolveFinalKey(key)
            if not finalKey in definitions:
                definitions[finalKey] = { "referencedBy": [] }
            if key == finalKey:
                for subKey in ["description", "default", "multiple", "references", "valuename"]:
                    definitions[finalKey][subKey] = self._opts[finalKey][subKey]
            else:
                definitions[finalKey]["referencedBy"].append(key)
                
        return definitions

    def clearOptionDefinitions(self):
        self._longopts = {}

    def addOptionDefinition(
        self, 
        argument,
        description = "",
        default = None,
        multiple = False,
        references = None,
        valuename = "VALUE"
    ):
        if not references is None:
            if not references in self._opts:
                raise ArgumentParserException("You cannot specify a reference \"" + references + "\" that does not exist for argument \"" + argument + "\"")
        self._opts[argument] = {
            "description": str(description),
            "default": default,
            "multiple": bool(multiple),
            "references": references,
            "valuename": str(valuename)
        }

    def resolveFinalKey(self, key):
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
        key = str(key)
        if value is None:
            value = opt["default"]

        # final key resolution
        key = self.resolveFinalKey(key)

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

        return (self.options, self.arguments)



class Application:
    _app = None
    _argparser = None

    name = None
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
        name = None
    ):
        self._app = app
        self._argparser = ArgumentParser(opts = opts)
        assert logger is None or isinstance(logger, logging.Logger), "logger is not a valid logging.Logger"
        self.logger = logger
        assert data is None or isinstance(data, QXSConsolas.Configuration.Configuration), "data is not a valid QXSConsolas.Configuration.Configuration"
        self.data = data
        assert configuration is None or isinstance(configuration, QXSConsolas.Configuration.Configuration), "data is not a valid QXSConsolas.Configuration.Configuration"
        self.configuration = configuration
        self.name = name

    def getHelpDict(self):
        return self._argparser.getCollapsedOptionDefinitions()


    def formatArgumentName(self, argumentName, valueName="VALUE"):
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
        s = self.formatArgumentName(argumentName, defBlock["valuename"])
        for arg in defBlock["referencedBy"]:
           s += ", " + self.formatArgumentName(arg, defBlock["valuename"])
        
        if not defBlock["default"] is None:
            s += "   (Default: " + str(defBlock["default"]) + ")"

        if defBlock["multiple"]:
            s += "   (Multiple times allowed)"

        if str(defBlock["description"]) != "":
            s += "\n    "
            s += "\n    ".join(str(defBlock["description"]).split("\n"))
        s += "\n"

        return s

    def showHelp(self, showName = True):
        definition = self._argparser.getCollapsedOptionDefinitions()
        if showName and not self.name is None:
            puts(self.name + "\n")
        for key in definition:
            puts(self.formatArgumentDefinitionBlock(key, definition[key]))

    def run(self, argv = None):
        self.options, self.arguments = self._argparser.parseArguments(argv)
        self._app(self)


def CliApp(
    Name = None,
    Opts = []
):
    assert isinstance(Opts, list), "Opts must be a list"
    for lopt in Opts:
        assert isinstance(lopt, dict), "every element in Opts must be a dict"
    def CliAppDecorator(func):
        @wraps(func)
        def FuncWrapper():
            return Application(app = func, opts = Opts, name = Name)
        return FuncWrapper
    return CliAppDecorator


