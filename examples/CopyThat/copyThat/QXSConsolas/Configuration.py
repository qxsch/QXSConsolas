#!/usr/bin/python

import os, yaml

class ConfigurationException(Exception):
    pass

class Configuration:
    configuaration = None

    def __init__(self, configFile = None, configData = None):
        if configFile is None and configData is None:
            raise ConfigurationException("You did not specify any arguments! Please use either a configFile or configData")
        if (not configFile is None) and (not configData is None):
            raise ConfigurationException("You did not specify both arguments! Please use either a configFile or configData")
        if configData is None:
            with open(configFile) as myfile:
                configData="\n".join(line.rstrip() for line in myfile)
            self.configuaration = yaml.load(configData)
        else:
            self.configuaration = configData

    def getValueAsConfiguration(self, path):
        return Configuration(configData = self.getValue(path))

    def pathExists(self, path):
        _cfg = self.configuaration
        try:
            for currentKey in path.split("."):
                _cfg = _cfg[currentKey]
            return True
        except:
            return False

    def getValue(self, path):
        _cfg = self.configuaration
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
        return yaml.dump(self.configuaration)

    def __getitem__(self, key):
        return Configuration(self.configuaration[key])
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

