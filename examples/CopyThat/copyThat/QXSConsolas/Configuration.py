#!/usr/bin/python

import os, yaml

class ConfigurationException(Exception):
    pass

class Configuration:
    configuaration = None

    def __init__(self, configFile):
        data=""
        with open(configFile) as myfile:
            data="\n".join(line.rstrip() for line in myfile)
        self.configuaration = yaml.load(data)

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

