#!/usr/bin/python

import os, yaml

class ConfigurationException(Exception):
    pass

class Configuration:
    configuration = None

    def __init__(self, configFile = None, configData = None):
        if configFile is None and configData is None:
            raise ConfigurationException("You did not specify any arguments! Please use either a configFile or configData")
        if (not configFile is None) and (not configData is None):
            raise ConfigurationException("You did not specify both arguments! Please use either a configFile or configData")
        if configData is None:
            with open(configFile) as myfile:
                configData="\n".join(line.rstrip() for line in myfile)
            self.configuration = yaml.load(configData)
        else:
            self.configuration = configData

    def get(self, path):
        val = self.getValue(path) 
        if isinstance(val, dict) or isinstance(val, list):
            return Configuration(configData = val)
        else:
            return val
    def pathExists(self, path):
        _cfg = self.configuration
        try:
            for currentKey in path.split("."):
                _cfg = _cfg[currentKey]
            return True
        except:
            return False

    def getValue(self, path):
        _cfg = self.configuration
        fullCurrentKey = []
        try:
            for currentKey in path.split("."):
		fullCurrentKey.append(currentKey)
                _cfg = _cfg[currentKey]
            return _cfg
        except:
            fullCurrentKey = ".".join(fullCurrentKey)
            if fullCurrentKey == path:
                raise ConfigurationException("The key \"" + fullCurrentKey + "\" does not exist exist.")
            else:
                raise ConfigurationException("The key \"" + fullCurrentKey + "\" does not exist and hence the key \"" + path + "\" does not exist.")

    def dump(self):
        return str(yaml.dump(self.configuration)).rstrip()

    def __getitem__(self, key):
        if isinstance(self.configuration[key], dict) or isinstance(self.configuration[key], list):
            return Configuration(configData = self.configuration[key])
        else:
            return self.configuration[key] 

    def __iter__(self):
        if isinstance(self.configuration, dict):
            for x in self.configuration:
                yield x
        elif isinstance(self.configuration, list):
            i = 0
            for x in self.configuration:
                yield i
                i = i + 1
        else:
            raise ConfigurationException("You cannot iterate a type that is not iteratable.")
    # https://docs.python.org/3/reference/datamodel.html?emulating-container-types#emulating-container-types


def GetSystemConfiguration():
    if GetSystemConfiguration._systemConfig is None:
        GetSystemConfiguration._systemConfig = Configuration(
            os.path.join(
                os.path.dirname(os.path.dirname(
                    os.path.realpath(__file__))
                ),
                "config.yaml"
            )
        )
    return GetSystemConfiguration._systemConfig

GetSystemConfiguration._systemConfig=None


def SysConf():
    return GetSystemConfiguration()

