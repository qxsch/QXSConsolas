#!/usr/bin/python

import logging, os
from QXSConsolas.Command import SSH, call
from clint.textui import puts, colored, indent
import timeit
import abc


class SplunkRole(object):
    __metaclass__ = abc.ABCMeta

    _app = None
    _appname = None
    _appdir = None
    _appconfig = None
    _envname = None
    _envconfig = None
    _rolename = None
    _roleconfig = None

    def setRoleInfo(self, cliapp, appname, appdir, appconfig, envname, envconfig, rolename, roleconfig):
	"""
        deploys the app to the server
        cliapp    QXSConsolas.Cli.ApplicationData
                  cli application data
        appname   string
                  name of the app, that should be deployed
        appdir    string
                  local dir of the app, that should be deployed
        appconfig QXSConsolas.Configuration.Configuration
                  configuration of the app, that should be deployed
        envname   string
                  name of the environment, where the app should be deployed
        envconfig QXSConsolas.Configuration.Configuration
                  configuration of the environment, where the app should be deployed
        rolename   string
                   name of the environment, where the app should be deployed
        roleconfig QXSConsolas.Configuration.Configuration
                   configuration of the role, where the app shoukd be deplyed
	"""
        self._app = cliapp
        self._appname = appname
        self._appdir = appdir
        self._appconfig = appconfig
        self._envname = envname
        self._envconfig = envconfig
        self._rolename = rolename
        self._roleconfig = roleconfig

    @abc.abstractmethod
    def deployAppToServer(self, ssh, remoteappdir, srvconfig):
	"""
        deploys the app to the server
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        remoteappdir string
                     the remote directory name of the application
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        pass


class SearchHeadRole(SplunkRole):
    def deployAppToServer(self, ssh, remoteappdir, srvconfig):
	"""
        deploys the app to the server
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        remoteappdir string
                     the remote directory name of the application
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        #print(self._envconfig.dump())
        print(srvconfig["hostname"] + " " + srvconfig["path"])


class IndexerRole(SplunkRole):
    def deployAppToServer(self, ssh, remoteappdir, srvconfig):
	"""
        deploys the app to the server
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        remoteappdir string
                     the remote directory name of the application
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        #print(self._envconfig.dump())
        print(srvconfig["hostname"] + " " + srvconfig["path"])


class UnifiedForwarderManagementRole(SplunkRole):
    def deployAppToServer(self, ssh, remoteappdir, srvconfig):
	"""
        deploys the app to the server
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        remoteappdir string
                     the remote directory name of the application
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        #print(self._envconfig.dump())
        print(srvconfig["hostname"] + " " + srvconfig["path"])


def getSplunkRoles():
    roles = {}

    roles["SHD"] = SearchHeadRole()
    roles["SearchHeadRole"] = roles["SHD"]
    roles["SearchHead"] = roles["SHD"]

    roles["IDX"] = IndexerRole()
    roles["IndexerRole"] = roles["IDX"]
    roles["Indexer"] = roles["IDX"]

    roles["UFM"] = UnifiedForwarderManagementRole()
    roles["UnifiedForwarderManagementRole"] = roles["UFM"]
    roles["UnifiedForwarderManagement"] = roles["UFM"]

    return roles    
