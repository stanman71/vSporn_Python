from pyVmomi import vim
from pyVmomi import vmodl
import getpass
import requests


class bcolors:

    HEADER =    '\033[95m'
    OKBLUE =    '\033[94m'
    OKGREEN =   '\033[92m'
    WARNING =   '\033[93m'
    FAIL =      '\033[91m'
    ENDC =      '\033[0m'
    BOLD =      '\033[1m'
    UNDERLINE = '\033[4m'


####################

#  wait_for_task

####################


def wait_for_task(task):
    
    """ wait for a vCenter task to finish """

    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result
 
        if task.info.state == 'error':
            print ("there was an error")
            task_done = True
 
 
####################

#     get_obj

####################


def get_obj(content, vimtype, name):

    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break
 
    return obj


####################

#   GET_VMHost

####################


def GET_VMHost(content, exsi):

    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)
    hosts = [host for host in host_view.view]
    host_view.Destroy()

    for host in hosts:
        if host.name == exsi:
            print(host)
            return host


####################

#     GET_VMs

####################


def GET_VMs(content):

    print("Getting all VMs ...")
    vm_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                      [vim.VirtualMachine],
                                                      True)
    obj = [vm for vm in vm_view.view]
    vm_view.Destroy()

    for vm in obj:
        print(vm.name)

    return obj
            

####################

#    Search_VM

####################


def Search_VM(content, VM_name):

    print("Checking all VMs ...")
    vm_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                      [vim.VirtualMachine],
                                                      True)
    obj = [vm for vm in vm_view.view]
    vm_view.Destroy()

    for vm in obj:

        if VM_name == vm.name:
            print(vm.name)
            return True
       
    return False


####################

#     Start_VM

####################


def Start_VM(content, VM_name):

    VM = get_obj(content, [vim.VirtualMachine], VM_name)

    if VM is None:
        raise SystemExit(bcolors.FAIL + "Unable to locate VirtualMachine." + bcolors.ENDC)
    
    print (bcolors.OKBLUE + "Found: {0}".format(VM.name) + bcolors.ENDC)
    print (bcolors.OKBLUE + "The current powerState is: {0}".format(VM.runtime.powerState) + bcolors.ENDC)
 
    if VM.runtime.powerState == "poweredOff": 
        TASK = VM.PowerOn()
        print (bcolors.OKGREEN + "VM " + VM_name + " started" + bcolors.ENDC)

        wait_for_task(TASK)
        print (bcolors.OKGREEN + "VM " + VM_name + " running" + bcolors.ENDC)


####################

#     Clone_VM

####################


def Clone_VM(
        content, vm_template, vm_name, resource_pool_name, datacenter_name, vm_folder, datastore_name, si,         
        cluster_name = "", power_on = False):


    # VM exist ?

    if Search_VM(content, vm_name) == True:
        print(bcolors.OKBLUE + "VM already exist" + bcolors.ENDC)
        return


    template = None
    template = get_obj(content, [vim.VirtualMachine], vm_template)

    if template == None:
        print(bcolors.FAIL + "NO valid template" + bcolors.ENDC)
        return

    resource_pool = None
    resource_pool = get_obj(content, [vim.ResourcePool], resource_pool_name)
   
    if resource_pool == None:
        print(bcolors.FAIL + "NO valid resource_pool" + bcolors.ENDC)
        return

    datacenter = None
    datacenter = get_obj(content, [vim.Datacenter], datacenter_name)

    if datacenter == None:
        print(bcolors.FAIL + "NO valid datacenter" + bcolors.ENDC)
        return

    destfolder = None
    destfolder = get_obj(content, [vim.Folder], vm_folder)
 
    if destfolder == None:
        print(bcolors.FAIL + "NO valid destfolder" + bcolors.ENDC)
        return

    datastore = None
    datastore = get_obj(content, [vim.Datastore], datastore_name)
 
    if datastore == None:
        print(bcolors.FAIL + "NO valid datastore" + bcolors.ENDC)
        return

 
    # if None, get the first one
    # cluster = get_obj(content, [vim.ClusterComputeResource], cluster_name) 


    # set relospec
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resource_pool
 
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = power_on
 
    print (bcolors.OKBLUE + "cloning VM..." + vm_name + bcolors.ENDC)
    
    task = template.Clone(folder=destfolder, name=vm_name, spec=clonespec)
    wait_for_task(task)

    # VM created ?

    if Search_VM(content, vm_name) == True:
        print(bcolors.OKGREEN + "VM " + vm_name + " successful created" + bcolors.ENDC)
        return

 
####################

#     GET_NICs

####################


def GET_NICs(content, VM_name):

    # Get VM

    def Search_VM(content, VM_name):

        vm_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.VirtualMachine],
                                                        True)
        obj = [vm for vm in vm_view.view]
        vm_view.Destroy()

        for vm in obj:

            if VM_name == vm.name:
                vm = vm
                return vm

    vm = Search_VM(content, VM_name)


    # Get Hosts

    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.HostSystem],
                                                            True)
    
    hosts = [host for host in host_view.view]
    host_view.Destroy()

    hostPgDict = {}


    # Get Portgroups

    for host in hosts:
        pgs = host.config.network.portgroup
        hostPgDict[host] = pgs

    Group = []


    for dev in vm.config.hardware.device:
        if isinstance(dev, vim.vm.device.VirtualEthernetCard):
            dev_backing = dev.backing
            portGroup = None
            vlanId = None
            vSwitch = None
            if hasattr(dev_backing, 'port'):
                portGroupKey = dev.backing.port.portgroupKey
                dvsUuid = dev.backing.port.switchUuid
                try:
                    dvs = content.dvSwitchManager.QueryDvsByUuid(dvsUuid)
                except:
                    portGroup = "** Error: DVS not found **"
                    vlanId = "NA"
                    vSwitch = "NA"
                else:
                    pgObj = dvs.LookupDvPortGroup(portGroupKey)
                    portGroup = pgObj.config.name
                    vlanId = str(pgObj.config.defaultPortConfig.vlan.vlanId)
                    vSwitch = str(dvs.name)
            else:
                portGroup = dev.backing.network.name
                vmHost = vm.runtime.host
                # global variable hosts is a list, not a dict
                host_pos = hosts.index(vmHost)
                viewHost = hosts[host_pos]
                # global variable hostPgDict stores portgroups per host
                pgs = hostPgDict[viewHost]
                for p in pgs:
                    if portGroup in p.key:
                        vlanId = str(p.spec.vlanId)
                        vSwitch = str(p.spec.vswitchName)
            if portGroup is None:
                portGroup = 'NA'
            if vlanId is None:
                vlanId = 'NA'
            if vSwitch is None:
                vSwitch = 'NA'
            
            Group.append(portGroup)

    return Group


####################

#     ADD_NIC

####################


def ADD_NIC(content, VM_name, network, si):

    # VM exist ?

    VM = get_obj(content, [vim.VirtualMachine], VM_name)

    if VM is None:
        raise SystemExit(bcolors.FAIL + "Unable to locate VirtualMachine " + VM_name + bcolors.ENDC)

    # NIC exist ?

    exist_networks = GET_NICs(content, VM_name)

    for check_network in exist_networks:
        if check_network == network:
            print (bcolors.WARNING + network + " at " + VM_name + " already exist" + bcolors.ENDC)
            return

    spec = vim.vm.ConfigSpec()
    nic_changes = []
 
    nic_spec = vim.vm.device.VirtualDeviceSpec()
    nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
 
    nic_spec.device = vim.vm.device.VirtualVmxnet3()
 
    nic_spec.device.deviceInfo = vim.Description()
    nic_spec.device.deviceInfo.summary = 'vCenter API test'

    nic_spec.device.backing = \
    vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
    nic_spec.device.backing.useAutoDetect = False
    content = si.RetrieveContent()
    nic_spec.device.backing.network = get_obj(content, [vim.Network], network)
    nic_spec.device.backing.deviceName = network
 
    nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    nic_spec.device.connectable.startConnected = True
    nic_spec.device.connectable.startConnected = True
    nic_spec.device.connectable.allowGuestControl = True
    nic_spec.device.connectable.connected = False
    nic_spec.device.connectable.status = 'untried'
    nic_spec.device.wakeOnLanEnabled = True
    nic_spec.device.addressType = 'assigned'
 
    nic_changes.append(nic_spec)
    spec.deviceChange = nic_changes
    
    try:
        VM.ReconfigVM_Task(spec=spec)
        print (bcolors.OKGREEN + "NIC CARD with Network " + network + " added to VM " + VM_name + bcolors.ENDC)
        return

    except:
        print (bcolors.FAIL + "Error VM " + VM_name + bcolors.ENDC)
        return


####################

#      DEL_VM

####################


def DEL_VM(content, VM_name):

    VM = get_obj(content, [vim.VirtualMachine], VM_name)

    if VM is None:
        raise SystemExit(bcolors.FAIL + "Unable to locate VirtualMachine." + bcolors.ENDC)
    
    print(bcolors.OKBLUE + "Found: {0}".format(VM.name) + bcolors.ENDC)
    print(bcolors.OKBLUE + "The current powerState is: {0}".format(VM.runtime.powerState) + bcolors.ENDC)

    if format(VM.runtime.powerState) == "poweredOn":
        print(bcolors.OKBLUE + "Attempting to power off {0}".format(VM.name) + bcolors.ENDC)
        TASK = VM.PowerOffVM_Task()  
        wait_for_task(TASK) 
        print(bcolors.OKGREEN + "{0}".format(TASK.info.state) + bcolors.ENDC)
    
    print(bcolors.OKBLUE + "Destroying VM from vSphere." + bcolors.ENDC)
    TASK = VM.Destroy_Task()
    wait_for_task(TASK)
    print(bcolors.OKGREEN + "Done." + bcolors.ENDC)
