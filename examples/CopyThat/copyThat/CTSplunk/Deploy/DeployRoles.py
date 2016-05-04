#!/usr/bin/python

import logging, os
from QXSConsolas.Command import SSH, call
from clint.textui import puts, colored, indent
import timeit
import abc
from urlparse import urlparse
from CTSplunk import NoRolesToDeployException, DeploymentException, AppNotFoundException

class SplunkRole(object):
    __metaclass__ = abc.ABCMeta

    app = None
    _envname = None
    _envconfig = None
    _rolename = None
    _roleconfig = None

    def setRoleInfo(self, cliapp, envname, envconfig, rolename, roleconfig):
	"""
        deploys the app to the server
        cliapp    QXSConsolas.Cli.ApplicationData
                  cli application data
        envname   string
                  name of the environment, where the app should be deployed
        envconfig QXSConsolas.Configuration.Configuration
                  configuration of the environment, where the app should be deployed
        rolename   string
                   name of the environment, where the app should be deployed
        roleconfig QXSConsolas.Configuration.Configuration
                   configuration of the role, where the app shoukd be deplyed
	"""
        self.app = cliapp
        self._envname = envname
        self._envconfig = envconfig
        self._rolename = rolename
        self._roleconfig = roleconfig

    @abc.abstractmethod
    def doBeforeDeployment(self, ssh, srvconfig):
	"""
        run code before apps will be deployed  (will run once for every server in affected env.role)
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        pass

    @abc.abstractmethod
    def deployAppToServer(self, ssh, appname, appdir, appconfig, remoteappdir, srvconfig):
	"""
        deploys an app to the server
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        appname      string
                     name of the app, that should be deployed
        appdir       string
                     local dir of the app, that should be deployed
        appconfig    QXSConsolas.Configuration.Configuration
                     configuration of the app, that should be deployed
        remoteappdir string
                     the remote directory name of the application
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        pass

    @abc.abstractmethod
    def doAfterDeployment(self, ssh, srvconfig):
	"""
        run code after apps were deployed (will run once for every server in affected env.role)
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        pass

    def _syncLocalAppToRemote(self, ssh, appdir, remoteappdir, srvconfig):
        # use rsync
        if ssh.host == "localhost":
            rc, stdout, stderr = call(["rsync", "--delete", "--stats", "--exclude", ".git*", "-az", appdir + "/", remoteappdir + "/"])
        else:
            rc, stdout, stderr = call(["rsync", "--delete", "--stats", "--exclude", ".git*", "-aze", "ssh", appdir + "/", ssh.host + ":" + remoteappdir + "/"])
        if rc == 0:
            self.app.logger.debug("Syncing the app to \"" + ssh.host + ":" + remoteappdir + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
            return True
        else:
            self.app.logger.error("Failed to sync the app to \"" + ssh.host + ":" + remoteappdir + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
            return False

    def _removeFileFromApp(self, ssh, remoteappdir, filename):
        rc, stdout, stderr = ssh.call(["find", remoteappdir, "-name", filename, "-print", "-delete" ])
        if rc == 0:
            if stdout.strip() != "":
                self.app.logger.warning("Deleted the following files on server \"" + ssh.host + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
        else:
            self.app.logger.error("Failed to delete file \"" + filename + "\" from app on server \"" + ssh.host + "\" with rc " + rc + ":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())


class SearchHeadRole(SplunkRole):
    def doBeforeDeployment(self, ssh, srvconfig):
        pass
    def deployAppToServer(self, ssh, appname, appdir, appconfig, remoteappdir, srvconfig):
	"""
        deploys the app to the server
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        appname      string
                     name of the app, that should be deployed
        appdir       string
                     local dir of the app, that should be deployed
        appconfig    QXSConsolas.Configuration.Configuration
                     configuration of the app, that should be deployed
        remoteappdir string
                     the remote directory name of the application
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        if not self._syncLocalAppToRemote(ssh, appdir, remoteappdir, srvconfig):
            raise DeploymentException("Failed to deploy the app to server \"" + ssh.host + "\"")
        self._removeFileFromApp(ssh, remoteappdir, "indexes.conf")

    def doAfterDeployment(self, ssh, srvconfig):
        # running the shd deployment
        url, user, password = splitUrlCreds(srvconfig)
        cmd = [ "splunk", "apply", "shcluster-bundle", "--answer-yes" ]
        if not (url is None or url == ""):
            cmd.append("-target")
            cmd.append(url)
        if not (user is None or user == "" or password is None or password == ""):
            cmd.append("-auth")
            cmd.append(user + ":" + password)
        rc, stdout, stderr = ssh.call(cmd)
        if rc == 0:
            self.app.logger.debug("Appling the SHD cluster-bundle on server \"" + ssh.host + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
        else:
            self.app.logger.error("Failed to apply the SHD cluster-bundle on server \"" + ssh.host + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())


class IndexerRole(SplunkRole):
    def doBeforeDeployment(self, ssh, srvconfig):
        pass
    def deployAppToServer(self, ssh, appname, appdir, appconfig, remoteappdir, srvconfig):
	"""
        deploys the app to the server
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        appname      string
                     name of the app, that should be deployed
        appdir       string
                     local dir of the app, that should be deployed
        appconfig    QXSConsolas.Configuration.Configuration
                     configuration of the app, that should be deployed
        remoteappdir string
                     the remote directory name of the application
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        if not self._syncLocalAppToRemote(ssh, appdir, remoteappdir, srvconfig):
            raise DeploymentException("Failed to deploy the app to server \"" + ssh.host + "\"")

    def doAfterDeployment(self, ssh, srvconfig):
        # running the idx deployment
        url, user, password = splitUrlCreds(srvconfig)
        cmd = [ "splunk", "apply", "cluster-bundle", "--answer-yes" ]
        # andy says: do not set a target
        #if not (url is None or url == ""):
        #    cmd.append("-target")
        #    cmd.append(url)
        if not (user is None or user == "" or password is None or password == ""):
            cmd.append("-auth")
            cmd.append(user + ":" + password)
        rc, stdout, stderr = ssh.call(cmd)
        if rc == 0:
            self.app.logger.debug("Appling the IDX cluster-bundle on server \"" + ssh.host + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
        else:
            self.app.logger.error("Failed to apply the IDX cluster-bundle on server \"" + ssh.host + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())


class UnifiedForwarderManagementRole(SplunkRole):
    def doBeforeDeployment(self, ssh, srvconfig):
        pass
    def deployAppToServer(self, ssh, appname, appdir, appconfig, remoteappdir, srvconfig):
	"""
        deploys the app to the server
        ssh          QXSConsolas.Command.SSH
                     the ssh connection to the host
        appname      string
                     name of the app, that should be deployed
        appdir       string
                     local dir of the app, that should be deployed
        appconfig    QXSConsolas.Configuration.Configuration
                     configuration of the app, that should be deployed
        remoteappdir string
                     the remote directory name of the application
        srvconfig    QXSConsolas.Configuration.Configuration
                     server configuration with hostname and path
	"""
        if not self._syncLocalAppToRemote(ssh, appdir, remoteappdir, srvconfig):
            raise DeploymentException("Failed to deploy the app to server \"" + ssh.host + "\"")
        self._removeFileFromApp(ssh, remoteappdir, "indexes.conf")

    def doAfterDeployment(self, ssh, srvconfig):
        # running the idx deployment
        url, user, password = splitUrlCreds(srvconfig)
        cmd = [ "splunk", "reload", "deploy-server", "--answer-yes" ]
        # andy says: do not set a target
        #if not (url is None or url == ""):
        #    cmd.append("-target")
        #    cmd.append(url)
        if not (user is None or user == "" or password is None or password == ""):
            cmd.append("-auth")
            cmd.append(user + ":" + password)
        rc, stdout, stderr = ssh.call(cmd)
        if rc == 0:
            self.app.logger.debug("Reloading the deploy-server on server \"" + ssh.host + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())
        else:
            self.app.logger.error("Failed to reload the deploy-server on server \"" + ssh.host + "\":\n" + (stdout.strip() + "\n" + stderr.strip()).strip())


def splitUrlCreds(url):
    if type(url) == str:
        target = urlparse(url)
    elif "target" in url:
        target = urlparse(url["target"])
    elif "url" in url:
        target = urlparse(url["url"])
    elif "credentials" in url:
        a = url["credentials"].split(":")
        if len(a) >= 2:
            return [ None, a[0], ":".join(a[1:]) ]
        else:
            return [ None, None, None ]
    else:
        return [ None, None, None ]
    url = ""
    if target.scheme == "":
        url += "http://"
    else:
        url += target.scheme + "://"
    if target.hostname is None or target.hostname == "":
        url += "localhost"
    else:
        url += target.hostname
    if not target.port is None:
        url += ":" + str(target.port)
    if target.path[0] != "/":
        url += "/"
    url += target.path
    if target.params != "":
        url += "?" + target.params
    if (type(url) != str) and ( target.username == "" or target.username is None or target.password == "" or target.password is None ):
        if "credentials" in url:
            a = url["credentials"].split(":")
            if len(a) >= 2:
                return [ url, a[0], ":".join(a[1:]) ]
            else:
                return [ url, target.username, target.password ]
    return [ url, target.username, target.password ]


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

def registerSplunkRole(key, role):
    if key in roles:
        raise KeyError("Cannot add a role to an existing key")
    if not isinstance(role, SplunkRole):
        raise TypeError("The specified role is not a SplunkRole")
    roles[key] = role

def getSplunkRoles():
    return roles

