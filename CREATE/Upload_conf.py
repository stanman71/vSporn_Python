import sys
from getpass import getpass
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import LockError
from jnpr.junos.exception import UnlockError
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.exception import CommitError
from jnpr.junos.utils.config import Config
import stopit



class bcolors:

    HEADER =    '\033[95m'
    OKBLUE =    '\033[94m'
    OKGREEN =   '\033[92m'
    WARNING =   '\033[93m'
    FAIL =      '\033[91m'
    ENDC =      '\033[0m'
    BOLD =      '\033[1m'
    UNDERLINE = '\033[4m'



def Upload_conf(input, hostname, username, password, mode = "telnet", port = 23, commant = "Commited by NetConf"):

    # Connect to the Host

    try:
        dev = Device(host = hostname, user = username, passwd = password, mode = mode, port = port)
        dev.open()

    except Exception as err:
        sys.exit(1)

    dev.bind(cu=Config)


    # Load configuration changes

    print (bcolors.OKBLUE + "Loading configuration changes" + bcolors.ENDC)
    
    try:
        dev.cu.load(input, merge=True)

    except (ConfigLoadError, Exception) as err:
        print (bcolors.WARNING + "Unable to load configuration changes: {0}".format(err) + bcolors.ENDC)
        return



    # Commit the configuration

    print (bcolors.OKGREEN + "Committing the configuration" + bcolors.ENDC)

    try: 
        dev.cu.commit(comment=commant)

    except CommitError as err:
        print (bcolors.WARNING + "Unable to commit configuration: {0}".format(err) + bcolors.ENDC)
        dev.close()
        return False 

    except ConnectionResetError as err:
        return False

    except RuntimeError as err:
        print (bcolors.WARNING + "Unable to connect: {0}".format(err) + bcolors.ENDC)
        return False

    print (bcolors.OKGREEN + "Configuration commited" + bcolors.ENDC)
    return True



    """

    with stopit.ThreadingTimeout(10) as to_ctx_mgr:
        assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
                    
        dev.cu.commit(comment=commant)


    print (bcolors.OKGREEN + "Configuration commited" + bcolors.ENDC)
    return True    

    """