from pyVmomi import vim

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

#     get_obj

####################



def get_obj(content, vimtype, name):
 
    # Get the vsphere object associated with a given text name

    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    
    for c in container.view:
        if c.name == name:
            obj = c
            break
    
    return obj


####################

#   GET_Switches

####################


def GET_Switches(content, esxi):

    host = None
    host = get_obj(content, [vim.HostSystem], esxi)

    if host == None:
        print(bcolors.FAIL + "Can't connect to " + esxi + bcolors.ENDC)
        return

    host_switch_dict = {}
    host_switch_dict = host.config.network.vswitch
 
    print (type(host_switch_dict))

    for vswitches in host_switch_dict:
        print(vswitches.name)


####################

#  GET_Portgroups

####################


def GET_Portgroups(content, esxi):

    host = None
    host = get_obj(content, [vim.HostSystem], esxi)

    if host == None:
        print(bcolors.FAIL + "Can't connect to " + esxi + bcolors.ENDC)
        return

    host_portgroup_dict = {}
    host_portgroup_dict = host.config.network.portgroup

    for portgroup in host_portgroup_dict:
        print(portgroup.spec.name)


####################

#  Search_Switch

####################


def Search_Switch(host, switch_name):
    
    if host == None:
        print(bcolors.FAIL + "Can't connect to " + esxi + bcolors.ENDC)
        return

    host_switch_dict = {}
    host_switch_dict = host.config.network.vswitch

    for vswitches in host_switch_dict:
        if vswitches.name == switch_name:
            return True


####################

# Search_Portgroup

####################


def Search_Portgroup(host, portgroup_name):
    
    if host == None:
        print(bcolors.FAIL + "Can't connect to " + esxi + bcolors.ENDC)
        return

    host_portgroup_dict = {}
    host_portgroup_dict = host.config.network.portgroup

    for portgroup in host_portgroup_dict:
        if portgroup.spec.name == portgroup_name:
            return True


####################

#   ADD_Switch

####################


def ADD_Switch(content, exsi, switch_name, num_ports = 10):
 
    host = get_obj(content, [vim.HostSystem], exsi)
    host_network_system = host.configManager.networkSystem

    if Search_Switch(host, switch_name):
        print(bcolors.WARNING + "Switch " + switch_name + " already exist" + bcolors.ENDC)
        return

    vss_spec = vim.host.VirtualSwitch.Specification()
    vss_spec.numPorts = num_ports

    try:
        host_network_system.AddVirtualSwitch(vswitchName=switch_name, spec=vss_spec)
        print (bcolors.OKGREEN + "Successfully created vSwitch " + switch_name + bcolors.ENDC)

    except:
        print (bcolors.FAIL + "Can't create " + switch_name + bcolors.ENDC)
        return


####################

#  ADD_Portgroup

####################


def ADD_Portgroup(content, exsi, switch_name, portgroup_name):

    host = get_obj(content, [vim.HostSystem], exsi)
    host_network_system = host.configManager.networkSystem

    if Search_Portgroup(host, portgroup_name):
        print(bcolors.WARNING + "Portgroup " + portgroup_name + " already exist" + bcolors.ENDC)
        return

    port_group_spec = vim.host.PortGroup.Specification()
    port_group_spec.name = portgroup_name
    port_group_spec.vlanId = 0
    port_group_spec.vswitchName = switch_name

    security_policy = vim.host.NetworkPolicy.SecurityPolicy()
    security_policy.allowPromiscuous = True
    security_policy.forgedTransmits = True
    security_policy.macChanges = False

    port_group_spec.policy = vim.host.NetworkPolicy(security=security_policy)

    try:
        host_network_system.AddPortGroup(portgrp=port_group_spec)
        print (bcolors.OKGREEN + "Successfully created PortGroup " + portgroup_name + bcolors.ENDC)

    except:
        print (bcolors.FAIL + "Can't create " + portgroup_name + bcolors.ENDC)
        return


####################

#    DEL_Switch

####################


def DEL_Switch(content, exsi, switch_name):

    host = get_obj(content, [vim.HostSystem], exsi)
    host_network_system = host.configManager.networkSystem

    if Search_Switch(host, switch_name) is not True:
        print(bcolors.WARNING + "Switch " + switch_name + " don't exist" + bcolors.ENDC)
        return

    try:
        host_network_system.RemoveVirtualSwitch(vswitchName=switch_name)    
        print (bcolors.OKGREEN + "vSwitch " + switch_name + "successfully deleted" + bcolors.ENDC)

    except:
        print(bcolors.FAIL + "Can't delete " + switch_name + bcolors.ENDC)

        
