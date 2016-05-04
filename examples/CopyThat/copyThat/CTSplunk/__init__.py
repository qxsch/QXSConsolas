#!/usr/bin/python


class NoRolesToDeployException(Exception):
    pass
class DeploymentException(Exception):
    pass
class AppAlreadyExistsException(Exception):
    pass
class AppNotFoundException(Exception):
    pass

