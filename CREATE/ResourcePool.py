from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vmodl
import atexit
import ssl


class bcolors:

    HEADER =    '\033[95m'
    OKBLUE =    '\033[94m'
    OKGREEN =   '\033[92m'
    WARNING =   '\033[93m'
    FAIL =      '\033[91m'
    ENDC =      '\033[0m'
    BOLD =      '\033[1m'
    UNDERLINE = '\033[4m'



def GET_Pools(content, esxi):

    i = 0

    while True:

        try:
            hostname = content.rootFolder.childEntity[0].hostFolder.childEntity[i].name

            if hostname == esxi:
                for pool in content.rootFolder.childEntity[0].hostFolder.childEntity[i].resourcePool.resourcePool:
                    print(pool.name)

                return ("")
                                     
        except:
            print(bcolors.FAIL + "Host not exist" + bcolors.ENDC)
            return
            
        i = i + 1



def Search_Pool(content, esxi, pool_name):

    i = 0

    while True:

        try:
            hostname = content.rootFolder.childEntity[0].hostFolder.childEntity[i].name

            if hostname == esxi:
                for pool in content.rootFolder.childEntity[0].hostFolder.childEntity[i].resourcePool.resourcePool:
                    if pool.name == pool_name:
                        return True
                                    
        except:
            return
            
        i = i + 1



def ADD_Pool(content, esxi, pool_name, cpu_limit, ram_limit):

    i = 0

    while True:

        try:
            hostname = content.rootFolder.childEntity[0].hostFolder.childEntity[i].name

            if hostname == esxi:

                if Search_Pool(content, esxi, pool_name) == True:
                    print(bcolors.WARNING + "Pool already exist" + bcolors.ENDC)
                    return

                host = content.rootFolder.childEntity[0].hostFolder.childEntity[i]

                configSpec = vim.ResourceConfigSpec()
                cpuAllocationInfo = vim.ResourceAllocationInfo()
                memAllocationInfo = vim.ResourceAllocationInfo()
                sharesInfo = vim.SharesInfo(level='normal')

                cpuAllocationInfo.reservation = int(cpu_limit / 2)
                cpuAllocationInfo.expandableReservation = False
                cpuAllocationInfo.shares = sharesInfo
                cpuAllocationInfo.limit = cpu_limit

                memAllocationInfo.reservation = int(ram_limit / 2)
                memAllocationInfo.expandableReservation = False
                memAllocationInfo.shares = sharesInfo
                memAllocationInfo.limit = ram_limit
                   
                configSpec.cpuAllocation = cpuAllocationInfo
                configSpec.memoryAllocation = memAllocationInfo

                try:
                    host.resourcePool.CreateResourcePool(pool_name, configSpec)  
                    print (bcolors.OKGREEN + "Pool successful created" + bcolors.ENDC)  
                    return  

                except:
                    print (bcolors.FAIL + "Pool NOT created" + bcolors.ENDC)  
                    return    

        except:
            print(bcolors.FAIL + "Host not exist" + bcolors.ENDC)
            return

        i = i + 1


def Get_TrashPool(content, esxi):

    i = 0

    # Host exist ?

    while True:

        try:
            hostname = content.rootFolder.childEntity[0].hostFolder.childEntity[i].name

            if hostname == esxi:

                j = 0

                # Get Trash Pool

                while True:

                    host = content.rootFolder.childEntity[0].hostFolder.childEntity[i]

                    try:
                        pool = host.resourcePool.resourcePool[j].name  

                        if pool == "TRASH":
                            return(j)

                    except:
                        print(bcolors.FAIL + "Trash Pool not found" + bcolors.ENDC)
                        return

                    j = j + 1

        except:
            print(bcolors.FAIL + "Host not exist" + bcolors.ENDC)
            return

        i = i + 1


    
def DEL_Pool(content, esxi, pool_name):

    i = 0

    # Host exist ?

    while True:

        try:
            hostname = content.rootFolder.childEntity[0].hostFolder.childEntity[i].name

            if hostname == esxi:

                if Search_Pool(content, esxi, pool_name) is not True:
                    print(bcolors.FAIL + "Resource Pool not exist" + bcolors.ENDC)
                    return

                j = 0

                # Get Delete Resource Pool

                while True:

                    host = content.rootFolder.childEntity[0].hostFolder.childEntity[i]

                    try:
                        del_pool = host.resourcePool.resourcePool[j].name  

                        if del_pool == pool_name:

                            target_list = []
                            target_list.append(host.resourcePool.resourcePool[j])
            
                            trash_pool = host.resourcePool.resourcePool[Get_TrashPool(content, esxi)]

                            try:
                                trash_pool.MoveIntoResourcePool(target_list)
                                print (bcolors.OKGREEN + "Resource Pool was moved into TRASH" + bcolors.ENDC)

                            except:
                                print (bcolors.FAIL + "Resource Pool NOT deleted" + bcolors.ENDC)  
                                return   

                            try:                           
                                trash_pool.DestroyChildren()

                            except:
                                print (bcolors.FAIL + "Resource Pool NOT deleted" + bcolors.ENDC)  
                                return 

                            print (bcolors.OKGREEN + "Resource Pool successful deleted" + bcolors.ENDC)  
                            return  

                    except:
                        print (bcolors.FAIL + "Resource Pool NOT deleted" + bcolors.ENDC)  
                        return    

                    j = j + 1

        except:
            print(bcolors.FAIL + "Host not exist" + bcolors.ENDC)
            return

        i = i + 1

