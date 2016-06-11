#!/usr/bin/python
from QXSConsolas.Cli import CliApp
from clint.textui import puts, colored, indent

class NoRolesToDeployException(Exception):
    pass
class BackupException(Exception):
    pass
class RestoreException(Exception):
    pass
class DeploymentException(Exception):
    pass
class AppAlreadyExistsException(Exception):
    pass
class AppNotFoundException(Exception):
    pass
class IndexAlreadyExistsException(Exception):
    pass
class IndexNotFoundException(Exception):
    pass


@CliApp(
    Name = "Dump the Configuration",
    Description = "Dump the CTSplunk Configuration",
)
def DumpConfig(app):
    showInventory = False
    try:
        app.configuration.get("SplunkInventory.datasource")
        showInventory = True
    except:
        pass
    if showInventory:
        inv = app.configuration.get("SplunkInventory")
        puts(colored.yellow("----------------------------------------------------"))
        puts(colored.yellow("INVENTORY CONFIGURATION"))
        puts(colored.yellow("----------------------------------------------------"))
        with indent():
            for ckey, helptxt in {"datasource": "SQL Alchemy datasource (database connection definition)"}.iteritems():
                if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                if ckey in inv:
                    puts(colored.red(str(ckey) + ": ") + str(inv[ckey]))
                else:
                    puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
        puts("")

    apps = app.configuration.get("SplunkDeployment.apps")
    puts(colored.yellow("----------------------------------------------------"))
    puts(colored.yellow("APP CONFIGURATION") + " " + colored.blue("# FOR DEPLOYMENTS"))
    puts(colored.yellow("----------------------------------------------------"))
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
    puts(colored.yellow("----------------------------------------------------"))
    puts(colored.yellow("ENV CONFIGURATION") + " " + colored.blue("# FOR DEPLOYMENTS"))
    puts(colored.yellow("----------------------------------------------------"))
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
                        for ckey, helptxt in {"prelocal": "Execute locally before deployment", "preremote": "Execute on the remote site before deployment", "postlocal": "Execute locally after deployment", "postremote": "Execute on the remote site after deployment"}.iteritems():
                            if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                            if ckey in envs[env][role]:
                                puts(colored.red(str(ckey) + ": "))
                                with indent():
                                     for cmd in envs[env][role][ckey]:
                                         puts(colored.red("- ") + str(envs[env][role][ckey][cmd].configuration))
                            else:
                                puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
                        for server in envs[env][role]["servers"]:
                            puts(colored.red("server: ") + server)
                            with indent():
                                for ckey, helptxt in {"hostname": "Target hostname", "path": "Path to the remote app directory", "target": "Target to reload/restart after deployments"}.iteritems():
                                    if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                                    if ckey in envs[env][role]["servers"][server]:
                                        puts(colored.red(str(ckey) + ": ") + str(envs[env][role]["servers"][server][ckey]))
                                    else:
                                        puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
                                for ckey, helptxt in {"exclude": "Exclude patterns from synchronization"}.iteritems():
                                    if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                                    if ckey in envs[env][role]["servers"][server]:
                                        puts(colored.red(str(ckey) + ": "))
                                        with indent():
                                            for i in envs[env][role]["servers"][server][ckey]:
                                                puts(colored.red("- ") + str(envs[env][role]["servers"][server][ckey][i]))
                                    else:
                                        puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
    puts("")

    envs = app.configuration.get("SplunkNodes.envs")
    puts(colored.yellow("----------------------------------------------------"))
    puts(colored.yellow("NODE CONFIGURATION") + " " + colored.blue("# FOR BACKUP/RESTORE & NODE TASKS"))
    puts(colored.yellow("----------------------------------------------------"))
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
                                for ckey, helptxt in {"hostname": "Target hostname", "path": "Path to the remote app directory", "target": "Target to reload/restart after deployments"}.iteritems():
                                    if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                                    if ckey in envs[env][role]["servers"][server]:
                                        puts(colored.red(str(ckey) + ": ") + str(envs[env][role]["servers"][server][ckey]))
                                    else:
                                        puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
                                for ckey, helptxt in {"exclude": "Exclude patterns from synchronization"}.iteritems():
                                    if str(helptxt) != "": puts(colored.blue("# " + str(helptxt)))
                                    if ckey in envs[env][role]["servers"][server]:
                                        puts(colored.red(str(ckey) + ": "))
                                        with indent():
                                            for i in envs[env][role]["servers"][server][ckey]:
                                                puts(colored.red("- ") + str(envs[env][role]["servers"][server][ckey][i]))
                                    else:
                                        puts(colored.red(str(ckey) + ": ") + colored.blue("## UNDEFINED ##"))
    puts("")

