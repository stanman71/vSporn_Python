from CREATE.Network import GET_Switches, GET_Portgroups, ADD_Switch, ADD_Portgroup, DEL_Switch
from CREATE.ResourcePool import GET_Pools, ADD_Pool, DEL_Pool
from CREATE.VM import GET_VMHost, GET_VMs, Search_VM, Start_VM, Clone_VM, GET_NICs, ADD_NIC, DEL_VM
from CREATE.Upload_conf import Upload_conf

from pyVim.connect import SmartConnect, Disconnect
from jnpr.junos import Device
import atexit
import sys
import ssl
import argparse
import yaml
import json
import time


class bcolors:

    HEADER =    '\033[95m'
    OKBLUE =    '\033[94m'
    OKGREEN =   '\033[92m'
    WARNING =   '\033[93m'
    FAIL =      '\033[91m'
    ENDC =      '\033[0m'
    BOLD =      '\033[1m'
    UNDERLINE = '\033[4m'


class Create_MAIN():

    def Create(File):

        # Open YAML-File

        with open(File, 'r') as ymlfile:
            myfile = yaml.load(ymlfile)


        # Connect to vCenter

        s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        s.verify_mode = ssl.CERT_NONE

        serviceInstance = SmartConnect(host = myfile['connection']["vcenter_ip"], 
                                    user = myfile['connection']["username"], 
                                    pwd  = myfile['connection']["password"], 
                                    sslContext = s)

        atexit.register(Disconnect, serviceInstance)
        content = serviceInstance.RetrieveContent()
    

        # Prepare Counter i, j

        num = len(myfile['devices'])

        i = 0
        j = -1


        # ADD Ressource Pool
    
        ADD_Pool(content, myfile['connection']["host_name"], myfile['project_name'], num * 3000, num * 2000)


        # Create Topology

        while j is not num:


            # Start VMs (i - 1)

            if j is not -1:   

                Start_VM(content, myfile['project_name'] + "_" + myfile['devices'][j]["name"] 
                                        + "_vCP_v"  + myfile['devices'][j]["version"])

                Start_VM(content, myfile['project_name'] + "_" + myfile['devices'][j]["name"] 
                                        + "_vFPC_v" + myfile['devices'][j]["version"]) 

            
            if i is not num:

                template_CP  = ""
                template_CP  = "TEMPLATE_vCP_"  + myfile['devices'][i]["version"]
                template_FPC = ""
                template_FPC = "TEMPLATE_vFPC_" + myfile['devices'][i]["version"]

                vm_name_CP  = ""  
                vm_name_CP  = (myfile['project_name'] + "_" + myfile['devices'][i]["name"] 
                                    + "_vCP_v"  + myfile['devices'][i]["version"])
                
                vm_name_FPC = "" 
                vm_name_FPC = (myfile['project_name'] + "_" + myfile['devices'][i]["name"] 
                                    + "_vFPC_v" + myfile['devices'][i]["version"])

                # Create internal network

                vSwitch            = myfile['project_name'] + "_Internal_" + myfile['devices'][i]["name"]
                int_portgroup_name = myfile['project_name'] + "_Internal_" + myfile['devices'][i]["name"]

                ADD_Switch(content,    myfile['connection']["host_name"], vSwitch)
                ADD_Portgroup(content, myfile['connection']["host_name"], vSwitch, int_portgroup_name)

                # Create external networks

                for m, network in enumerate(myfile['devices'][i]["network"]):

                    vSwitch            = myfile['project_name'] + "_External_" + network
                    ext_portgroup_name = myfile['project_name'] + "_External_" + network

                    ADD_Switch(content,    myfile['connection']["host_name"], vSwitch)
                    ADD_Portgroup(content, myfile['connection']["host_name"], vSwitch, ext_portgroup_name)

                # Clone VMs

                Clone_VM(content, template_CP,  vm_name_CP,  
                        myfile['project_name'], 
                        myfile['connection']["data_center"], 
                        myfile['connection']["vm_folder"], 
                        myfile['connection']["datastore"],
                        serviceInstance)
                
                Clone_VM(content, template_FPC, vm_name_FPC, 
                        myfile['project_name'], 
                        myfile['connection']["data_center"], 
                        myfile['connection']["vm_folder"], 
                        myfile['connection']["datastore"],
                        serviceInstance)

                # ADD NICs

                # br-ext
                ADD_NIC(content, vm_name_CP,  myfile['default_settings_TEMPLATE']['external_interface'], serviceInstance) 
                ADD_NIC(content, vm_name_FPC, myfile['default_settings_TEMPLATE']['external_interface'], serviceInstance) 

                # internal
                ADD_NIC(content, vm_name_CP,  int_portgroup_name, serviceInstance)      
                ADD_NIC(content, vm_name_FPC, int_portgroup_name, serviceInstance)     

                # external networks
                for n, network in enumerate(myfile['devices'][i]["network"]):

                    ext_portgroup_name = myfile['project_name'] + "_External_" + network
                    ADD_NIC(content, vm_name_FPC, ext_portgroup_name, serviceInstance) 


            # Upload config (i - 1)

            if j is not -1:    

                input = """
                    <configuration>
                            <system>
                                <host-name operation="delete"/>
                                <host-name operation="create">NEW_hostname</host-name>
                            </system>
                            <interfaces>
                                <interface>
                                    <name>fxp0</name>
                                    <unit>
                                        <name>0</name>
                                        <family>
                                            <inet>
                                                <address operation="delete">
                                                </address>
                                                <address insert="first" operation="create">
                                                    <name>NEW_mgmt_IP</name>
                                                </address>
                                            </inet>
                                        </family>
                                    </unit>
                                </interface>
                            </interfaces>
                            <routing-options>
                                <static>
                                    <route>
                                        <name>0.0.0.0/0</name>
                                        <next-hop operation="delete"></next-hop>
                                        <next-hop operation="create">NEW_gateway_IP</next-hop>
                                    </route>
                                </static>
                            </routing-options>
                    </configuration> """

                input = input.replace("NEW_hostname",   myfile['devices'][j]["name"])
                input = input.replace("NEW_mgmt_IP",    myfile['devices'][j]["mgmt_ip"])
                input = input.replace("NEW_gateway_IP", myfile['devices'][j]["mgmt_ip_gw"])   

                state = False

                while state == False:                
                        
                    try:
                                        
                        state = Upload_conf(input, 
                                            myfile['default_settings_TEMPLATE']['template_mgmt_IP'], 
                                            myfile['default_settings_TEMPLATE']['default_username'], 
                                            myfile['default_settings_TEMPLATE']['default_password']) 

                        input = ""

                    except:
                        pass
                                    
                    time.sleep(30)

            print("")
            print("")
            print("-------------------------------------------------------------------------------")
            print("")
            print("")

            i = i + 1
            j = i - 1

        print("VMs successful created")
        return


        ##################################
        ##################################


        # Possible variables 
            


        # vCenter

        #vCenter  = ""
        #username = ""
        #password = ""

        # Default settings

        #template_mgmt_IP = "172.18.10.85"
        #default_username = "netconf"
        #default_password = "netconf"
        #external_interface = "br-ext"

        # VM

        #vm_template        = "TEMPLATE_vCP_18.2R1.9"
        #vm_name            = "VM_Test"
        #resource_pool_name = "OSPF_01"
        #datacenter_name    = "Datacenter"
        #vm_folder          = "Xperience"
        #datastore_name     = "172.18.10.80"

        # Resource Pool

        #esxi               = "172.18.10.80"
        #pool_name          = "Test_Pool"
        #new_pool_name      = "Test_Pool"

        # Network

        #esxi               = "172.18.10.80"
        #vSwitch            = "Test_Switch"
        #portgroup_name     = "br-ext"



        # ---
        # VM
        # ---

        #GetVMHost(content, "172.18.10.80")

        #GET_VMs(content)

        #Search_VM(content, "vMX_E04_CP_18.2R1.9")

        #Start_VM(content, "vMX_E04_FPC_18.2R1.9")

        #Clone_VM(content, vm_template, vm_name, resource_pool_name, datacenter_name, vm_folder, datastore_name, serviceInstance)
    
        #GET_NICs(content, "vMX_E03_FPC_18.2R1.9")
    
        #ADD_NIC(content, "vMX_E03_FPC_18.2R1.9", "Inter E03", serviceInstance)

        #DEL_VM(content, vm_name)


        # -------------
        # Resource Pool
        # -------------


        #GET_Pools(content, esxi)

        #ADD_Pool(content, "172.18.10.80", "Test8", 1000, 1000)

        #DEL_Pool(content, esxi, "Test8")



        # -------
        # NETWORK
        # -------


        #GET_Switches(content, esxi)

        #GET_Portgroups(content, esxi)
        
        #ADD_Switch(content, esxi, vSwitch)

        #ADD_Portgroup(content, esxi, vSwitch, portgroup_name)

        #DEL_Switch(content, esxi, "Test9")
    

