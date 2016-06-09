#!/usr/bin/python
from QXSConsolas.Cli import CliApp
from clint.textui import puts, colored, indent

class NoRolesToDeployException(Exception):
    pass
class DeploymentException(Exception):
    pass
class AppAlreadyExistsException(Exception):
    pass
class AppNotFoundException(Exception):
    pass

@CliApp(
    Name = "Dump the Configuration",
    Description = "Dump the CTSplunk Configuration",
)
def DumpConfig(app):
    apps = app.configuration.get("SplunkDeployment.apps")
    puts("APP CONFIGURATION")
    with indent():
        for appname in apps:
            puts(colored.red("app: ") + colored.green(appname))
            for ckey, helptxt in {"directory": "Local app directory"}.iteritems():
                with indent():
                    if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                    if ckey in apps[appname]:
                        puts(colored.red(str(ckey) + ": ") + str(apps[appname][ckey]))
                    else:
                        puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
    puts("")
    envs = app.configuration.get("SplunkDeployment.envs")
    puts("ENV CONFIGURATION")
    with indent():
        for env in envs:
            puts(colored.red("env: ") + colored.green(env))
            with indent():
                for role in envs[env]:
                    puts(colored.red("role: ") + colored.green(role))
                    with indent():
                        for ckey, helptxt in {"role": "Deployment role"}.iteritems():
                            if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                            if ckey in envs[env][role]:
                                puts(colored.red(str(ckey) + ": ") + str(envs[env][role][ckey]))
                            else:
                                puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
                        for server in envs[env][role]["servers"]:
                            puts(colored.red("server: ") + server)
                            with indent():
                                for ckey, helptxt in {"hostname": "", "path": "Path to the remote app directory", "target": "Target to reload/restart after deployments"}.iteritems():
                                    if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                                    if ckey in envs[env][role]["servers"][server]:
                                        puts(colored.red(str(ckey) + ": ") + str(envs[env][role]["servers"][server][ckey]))
                                    else:
                                        puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
    puts("")

