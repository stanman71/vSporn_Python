import sys
from getpass import getpass
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from jnpr.junos.exception import LockError
from jnpr.junos.exception import UnlockError
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.exception import CommitError
from jnpr.junos.utils.config import Config
from pprint import pprint
import json


class bcolors:

    HEADER =    '\033[95m'
    OKBLUE =    '\033[94m'
    OKGREEN =   '\033[92m'
    WARNING =   '\033[93m'
    FAIL =      '\033[91m'
    ENDC =      '\033[0m'
    BOLD =      '\033[1m'
    UNDERLINE = '\033[4m'


class Juniper_MOD:

    hostname = ""
    username = ""
    password = ""
    mode     = ""
    port     = ""


    def __init__(self, hostname, username, password, mode, port):

        self.hostname = hostname
        self.username = username
        self.password = password
        self.mode     = mode
        self.port     = port

        global list_protocols
        list_protocols = ["stp","ospf","isis","bgp","mpls","lpd","rsvp","lldp","bfd"]

        global list_interfaces
        list_interfaces = ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2", "ge-0/0/3", "ge-0/0/4", "ge-0/0/5", 
                           "ge-0/0/6", "ge-0/0/7", "ge-0/0/8", "ge-0/0/9", "lo0", "fxp0"]

        global list_firewall_family
        list_firewall_family = ["any","inet","inet6","mpls","vpls","bridge","ethernet-switching"]



#----------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------- get_conf -----------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------



    def GET_conf(self, item):

 
        # Connect to the Host

        try:
            dev = Device(host=self.hostname, user=self.username, passwd=self.password, mode=self.mode, port=self.port)
            dev.open()
        except Exception as err:
            print (err)
            sys.exit(1)

        data = dev.rpc.get_config(options={'format':'json'})



        # get policy

        policys_name = data["configuration"]["policy-options"]["policy-statement"]

        for i, policy in enumerate(policys_name):
            pol_name = data["configuration"]["policy-options"]["policy-statement"][i]["name"]

            if item == pol_name:
                pprint(policys_name[i])
                return
            


        # get firewall

        output = []

        for firewall_typ in list_firewall_family:

            for i in range(0, 20):

                try:
                    firewall_name = data["configuration"]["firewall"]["family"][firewall_typ]["filter"][i]["name"]
                    output.append(firewall_name)

                    if item == firewall_name:
                        pprint(data["configuration"]["firewall"]["family"][firewall_typ]["filter"][i])
                        return

                except:
                    pass

        if item == "firewall" or item == "firewalls" or item == "Firewall" or item == "Firewalls":
            
            if output == []:
                print(bcolors.FAIL + "No Firewalls found" + bcolors.ENDC)
                return
            
            else:
                pprint(output)
                return    

                

        # only small letters
        item = item.lower()


        # get configuration

        if item == "":
            try:
                pprint(data["configuration"])
                
            except Exception as err:
                print (bcolors.FAIL + err + bcolors.ENDC)
            return



        # get hostname

        if item == "hostname" or item == "host-name":

            try:
                pprint(data["configuration"]["system"]["host-name"])
            except Exception as err:
                print (bcolors.FAIL + "No Hostname found" + bcolors.ENDC)
            return

  

        # get router-id   

        if item == "router-id" or item == "id":

            try:
                pprint(data["configuration"]["routing-options"]["router-id"])
            except Exception as err:
                print (bcolors.FAIL + "No Router-ID found" + bcolors.ENDC)
            return



        # get protocols

        if item == "protocols" or item == "protocol" or item in list_protocols:

            output = []
            temp = 0
            protocols = data["configuration"]["protocols"]
            
            for i, protocol in enumerate(protocols):              
                output.append(protocol)                   

            if item == "protocols" or item == "protocol":
                pprint(output)
                return

            if item in list_protocols:
   
                if item in output:  
                    protocol = data["configuration"]["protocols"][item]
                    pprint (item)
                    pprint (protocol)
                    return

                else:
                    print (bcolors.FAIL + "Protocol not activated" + bcolors.ENDC)
                    return


 
        # get policys

        if item == "policys" or item == "policy":

            output = []
            temp = 0
            policys = data["configuration"]["policy-options"]["policy-statement"]
            
            for i, policy in enumerate(policys):              
                output.append(data["configuration"]["policy-options"]["policy-statement"][i]["name"])                     
            pprint(output)
            return
   


        # get interfaces

        if item == "interfaces" or item == "interface" or item in list_interfaces:

            output = []
            temp = 0
            interfaces = data["configuration"]["interfaces"]["interface"]
            
            for i, interface in enumerate(interfaces):
                
                output.append(interface["name"])    

                try:
                    output.append(interface["unit"][0]["family"]["inet"]["address"][0]["name"])
                except:
                    output.append("NO IP-ADDRESS")
                
                output.append("----------------")


            if item == "interfaces" or item == "interface":
                pprint(output)
                return

            if item in list_interfaces:
    
                if item in output:
                    temp = output.index(item)
                    temp += 1
                    pprint(output[temp])
                    return

                else:
                    print (bcolors.FAIL + "Interface not found" + bcolors.ENDC)
                    return

 

        # no matches

        else:
            print(bcolors.FAIL + item + " >>> Wrong Input, ITEM not existing" + bcolors.ENDC)


        # End the NETCONF session and close the connection                    
        dev.close()


#----------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------- set_conf -----------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------


    def SET_conf(self, filename, commant = "Commited by NetConf"):


        # Connect to the Host

        try:
            dev = Device(host=self.hostname, user=self.username, passwd=self.password, mode=self.mode, port=self.port)
            dev.open()
        except Exception as err:
            print (err)
            sys.exit(1)

        dev.bind(cu=Config)


        # Lock the configuration

        print (bcolors.OKBLUE + "Locking the configuration" + bcolors.ENDC)

        try:
            dev.cu.lock()
        except LockError as err:
            print (bcolors.WARNING + "Unable to lock configuration: {0}".format(err) + bcolors.ENDC)
            dev.close()
            return


        # Load configuration changes

        print (bcolors.OKBLUE + "Loading configuration changes" + bcolors.ENDC)
        try:
            dev.cu.load(path=filename, merge=True)

        except (ConfigLoadError, Exception) as err:
            print (bcolors.WARNING + "Unable to load configuration changes: {0}".format(err) + bcolors.ENDC)
            try:
                dev.cu.unlock()
            except UnlockError:
                print (bcolors.WARNING + "Unable to unlock configuration: {0}".format(err) + bcolors.ENDC)
            dev.close()
            return


        # Commit the configuration

        print (bcolors.OKGREEN + "Committing the configuration" + bcolors.ENDC)

        try:
            dev.cu.commit(comment=commant)
        except CommitError as err:
            print (bcolors.WARNING + "Unable to commit configuration: {0}".format(err) + bcolors.ENDC)
            print ("Unlocking the configuration")
            try:
                dev.cu.unlock()
            except UnlockError as err:
                print (bcolors.WARNING + "Unable to unlock configuration: {0}".format(err) + bcolors.ENDC)
            dev.close()
            return


        # Unlock the configuration

        print (bcolors.OKBLUE + "Unlocking the configuration" + bcolors.ENDC)
        try:
            dev.cu.unlock()
        except UnlockError as err:
            print (bcolors.WARNING + "Unable to unlock configuration: {0}".format(err) + bcolors.ENDC)


        # End the NETCONF session and close the connection
        dev.close()


#----------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------- del_conf -----------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

    # Get XML-Delete statement in JUNOS
    # show | compare | display xml

   
    def DEL_conf(self, item):


        def upload_input(self, input):

            # Lock the configuration

            print (bcolors.OKBLUE + "Locking the configuration" + bcolors.ENDC)

            try:
                dev.cu.lock()
            except LockError as err:
                print (bcolors.WARNING + "Unable to lock configuration: {0}".format(err) + bcolors.ENDC)
                dev.close()
                return 1


            # Load configuration changes

            print (bcolors.OKBLUE + "Loading configuration changes" + bcolors.ENDC)
            try:
                dev.cu.load(input, merge=True)

            except (ConfigLoadError, Exception) as err:
                print (bcolors.WARNING + "Unable to load configuration changes: {0}".format(err) + bcolors.ENDC)
                try:
                    dev.cu.unlock()
                except UnlockError:
                    print (bcolors.WARNING + "Unable to unlock configuration: {0}".format(err) + bcolors.ENDC)
                dev.close()
                return 1


            # Commit the configuration

            print (bcolors.OKGREEN + "Committing the configuration" + bcolors.ENDC)

            try:
                dev.cu.commit(comment=commant)
            except CommitError as err:
                print (bcolors.WARNING + "Unable to commit configuration: {0}".format(err) + bcolors.ENDC)
                print ("Unlocking the configuration")
                try:
                    dev.cu.unlock()
                except UnlockError as err:
                    print (bcolors.WARNING + "Unable to unlock configuration: {0}".format(err) + bcolors.ENDC)
                dev.close()
                return 1


            # Unlock the configuration

            print (bcolors.OKBLUE + "Unlocking the configuration" + bcolors.ENDC)
            try:
                dev.cu.unlock()
            except UnlockError as err:
                print (bcolors.WARNING + "Unable to unlock configuration: {0}".format(err) + bcolors.ENDC)
                return 1


        # Check Delete statement

        if "delete" not in item:
            print(bcolors.FAIL + "Missing 'Delete' Statement" + bcolors.ENDC)
            return

        temp = item.split()
        item = temp[1]

        input = ""


        # Connect to the Host

        try:
            dev = Device(host=self.hostname, user=self.username, passwd=self.password, mode=self.mode, port=self.port)
            dev.open()
        except Exception as err:
            print (err)
            sys.exit(1)


        data = dev.rpc.get_config(options={'format':'json'})

        dev.bind(cu=Config)

        

        # Delete policy
    
        # Policy exist ?

        policys_name = data["configuration"]["policy-options"]["policy-statement"]

        for i, policy in enumerate(policys_name):
            pol_name = data["configuration"]["policy-options"]["policy-statement"][i]["name"]


            # Search policy in protocols

            if item == pol_name:
                
                output_result = []

                protocols = data["configuration"]["protocols"]

                # Check all protocols

                for i, protocol in enumerate(protocols):              
                    protocol_name = protocol  

                    # Check all policys

                    for i, policy in enumerate(pol_name):

                        # Search in BGP

                        if protocol_name == "bgp":

                            bgp_group = data["configuration"]["protocols"][protocol_name]["group"]

                            # Search BGP-Groups

                            for j, group in enumerate(bgp_group):

                                # Case: Export

                                try:
                                    policy_get = data["configuration"]["protocols"][protocol_name]["group"][j]["export"][i] 

                                    if policy_get == item: 
                                        output_result.append("bgp")
                                        output_result.append(data["configuration"]["protocols"][protocol_name]["group"][j]["name"])
                                        output_result.append("export")
                                                                                                    
                                except:
                                    ""                       

                                # Case: Import

                                try:
                                    policy_get = data["configuration"]["protocols"][protocol_name]["group"][j]["import"][i] 

                                    if policy_get == item:
                                        output_result.append("bgp")
                                        output_result.append(data["configuration"]["protocols"][protocol_name]["group"][j]["name"])
                                        output_result.append("import")
                                                                                    
                                except:
                                    ""

                        # Search in other protocols

                        else:

                            try:
                                policy_get = data["configuration"]["protocols"][protocol_name]["export"][i]    

                                if policy_get == item:  
                                    output_result.append(protocol_name)
                                    output_result.append("export") 
                                        
                            except:
                                ""                      

                            try:
                                policy_get = data["configuration"]["protocols"][protocol_name]["import"][i]    

                                if policy_get == item:  
                                    output_result.append(protocol_name)
                                    output_result.append("import")  
                                        
                            except:
                                ""
            
                # Result with policy entries in protocols
                # print(output_result)

                # Delete policy enties in protocols

                for i, protocol in enumerate(output_result):

                    # Delete policy entry in BGP

                    if output_result[i] == "bgp":
                                         
                        input = """
                            <configuration>
                                <protocols>
                                    <bgp>
                                        <group>
                                            <name>bgp_group</name>
                                            <type operation="delete">pol_name</type>
                                        </group>
                                    </bgp>
                                </protocols>
                            </configuration> """

                        input = input.replace("bgp_group", output_result[i+1])
                        input = input.replace("type", output_result[i+2])
                        input = input.replace("pol_name", item)

                        print(bcolors.OKGREEN + "Policy found in BGP, GROUP " + output_result[i+1] + " " + output_result[i+2] + " " + item + bcolors.ENDC)

                        commant = "Deleted " + item
                    
                        result = upload_input(self, input)

                        if result == None:
                            print(bcolors.OKGREEN + item + " in GROUP " + output_result[i+1] + " deleted" + bcolors.ENDC)

                        else:
                            print(bcolors.FAIL + item + " in GROUP " + output_result[i+1] + " NOT deleted" + bcolors.ENDC)
                            # End the NETCONF session and close the connection
                            dev.close()
                            return    

                        pprint("")

                        input = ""

                    # Delete policy entry in OSPF / ISIS

                    if output_result[i] == "ospf" or  output_result[i] == "isis":
                                         
                        input = """
                            <configuration>
                                    <protocols>
                                        <protocol_name>
                                            <type operation="delete">pol_name</type>
                                        </protocol_name>
                                    </protocols>
                            </configuration> """

                        input = input.replace("protocol_name", output_result[i])
                        input = input.replace("type", output_result[i+1])
                        input = input.replace("pol_name", item)       

                        print(bcolors.OKGREEN + "Policy found in " + output_result[i] + " " + output_result[i+1] + " " + item + bcolors.ENDC)

                        commant = "Deleted " + item

                        result = upload_input(self, input)

                        if result == None:
                            print(bcolors.OKGREEN + item + " in Protocol " + output_result[i] + " deleted" + bcolors.ENDC)

                        else:
                            print(bcolors.FAIL + item + " in Protocol " + output_result[i] + " NOT deleted" + bcolors.ENDC)
                            # End the NETCONF session and close the connection
                            dev.close()
                            return    

                        pprint("")

                        input = ""


                # Delete Policy

                print(bcolors.OKGREEN + "Delete Policy " + item + bcolors.ENDC)

                input= """
                <configuration>
                        <policy-options>
                            <policy-statement operation="delete">
                                <name>policy_name</name>
                            </policy-statement>
                        </policy-options>
                </configuration> """
            
                input = input.replace("policy_name", item)

                commant = "Deleted " + item

                result = upload_input(self, input)

                # End the NETCONF session and close the connection
                dev.close()

                if result == None:
                    print(bcolors.OKGREEN + item + " Deleted" + bcolors.ENDC)

                else:
                    print(bcolors.FAIL + item + "not Deleted" + bcolors.ENDC)                    

                return




        # Delete firewall
    
        # get Firewalls

        output_firewalls = []

        for firewall_typ in list_firewall_family:

            for i in range(0, 20):

                try:
                    firewall_name = data["configuration"]["firewall"]["family"][firewall_typ]["filter"][i]["name"]
                    output_firewalls.append(firewall_name)

                except:
                    pass

        # Firewall exist ?

        for firewall in output_firewalls:
           
            if item == firewall:
                                  
                output_result = []
                output_interfaces = []

                # get Interfaces

                interfaces = data["configuration"]["interfaces"]["interface"]
                
                for i, interface in enumerate(interfaces):
                    
                    try:
                        output_interfaces.append(data["configuration"]["interfaces"]["interface"][i]["name"])

                    except:
                        pass


                # Check all interfaces

                for i, interface in enumerate(output_interfaces):   

                    # Check all firewall types

                    for typ in list_firewall_family:

                        # Case: Input

                        try:                           
                            firewall_check = data["configuration"]["interfaces"]["interface"][i]["unit"][0]["family"][typ]["filter"]["input"]["filter-name"]
                                    
                            if firewall_check == item:  

                                output_result.append(interface)
                                output_result.append(typ)
                                output_result.append("input")

                        except:
                            pass

                        # Case: Output

                        try:                           
                            firewall_check = data["configuration"]["interfaces"]["interface"][i]["unit"][0]["family"][typ]["filter"]["output"]["filter-name"]

                            if firewall_check == item:  

                                output_result.append(interface)
                                output_result.append(typ)
                                output_result.append("output")

                        except:
                            pass

                # Result                        
                # pprint(output_result)

                # Delete Firewall entries in interfaces
           
                for i, element in enumerate(output_result):

                    if element in list_interfaces:

                        print(bcolors.OKGREEN + item + " found in " + output_result[i] + bcolors.ENDC)

                        input = """
                            <configuration>
                                    <interfaces>
                                        <interface>
                                            <name>interface_name</name>
                                            <unit>
                                                <name>0</name>
                                                <family>
                                                    <firewall_type>
                                                        <filter>
                                                            <firewall_direction operation="delete"/>
                                                        </filter>
                                                    </firewall_type>
                                                </family>
                                            </unit>
                                        </interface>
                                    </interfaces>
                            </configuration> """

                        input = input.replace("interface_name", output_result[i])
                        input = input.replace("firewall_type", output_result[i+1])
                        input = input.replace("firewall_direction", output_result[i+2])

                        commant = "Deleted " + item

                        result = upload_input(self, input)

                        if result == None:
                            print(bcolors.OKGREEN + item + " in " + output_result[i] + " deleted" + bcolors.ENDC)

                        else:
                            print(bcolors.FAIL + item + " in " + output_result[i] + " NOT deleted" + bcolors.ENDC)
                            # End the NETCONF session and close the connection
                            dev.close()
                            return    

                        pprint("")

                        input = ""  


                # Delete Firewall 

                print(bcolors.OKGREEN + " Delete " + item + " Firewall" + bcolors.ENDC)

                input = """
                    <configuration>
                            <firewall>
                                <family>
                                    <firewall_type>
                                        <filter operation="delete">
                                            <name>firewall_name</name>
                                        </filter>
                                    </firewall_type>
                                </family>
                            </firewall> 
                    </configuration> """


                # Get Firewall type

                for firewall_typ in list_firewall_family:

                    for i in range(0, 20):

                        try:
                            firewall_name_check = data["configuration"]["firewall"]["family"][firewall_typ]["filter"][i]["name"]
                            
                            if firewall_name_check == item:
                                firewall_result = firewall_typ
        
                        except:
                            pass

                input = input.replace("firewall_type", firewall_result)
                input = input.replace("firewall_name", item)
                        
                commant = "Deleted " + item

                result = upload_input(self, input)

                if result == None:
                    print(bcolors.OKGREEN + "Firewall " + item + " deleted" + bcolors.ENDC)
                    # End the NETCONF session and close the connection
                    dev.close()  
                    return        

                else:
                    print(bcolors.FAIL + "Firewall " + item + " NOT deleted" + bcolors.ENDC)
                    # End the NETCONF session and close the connection
                    dev.close()
                    return 



        # only small letters
        item = item.lower()


        # delete interface

        if "ge-" in item or item == "fxp0" or item == "lo0": 

            input= """
                <configuration>
                    <interfaces>
                        <interface>
                            <name>temp</name> 
                            <unit operation="delete">
                            </unit>    
                        </interface>
                    </interfaces>
                </configuration>"""

            
            input = input.replace("temp", item)

            commant = "Deleted " + item

            result = upload_input(self, input)

            # End the NETCONF session and close the connection
            dev.close()

            if result == None:
                print(bcolors.OKGREEN + item + " Deleted" + bcolors.ENDC)
 
            else:
                print(bcolors.FAIL + item + "not Deleted" + bcolors.ENDC)  

            return           



        # delete hostname

        if item == "hostname" or item == "host-name": 

            input= """
                    <system>
                        <host-name operation="delete"></host-name>
                    </system>"""
            

            commant = "Deleted " + item

            result = upload_input(self, input)

            # End the NETCONF session and close the connection
            dev.close()

            if result == None:
                print(bcolors.OKGREEN + item + " Deleted" + bcolors.ENDC)
 
            else:
                print(bcolors.FAIL + item + "not Deleted" + bcolors.ENDC)  

            return
            


        #delete router-id

        if item == "router-id" or item == "id":

            input= """
                    <routing-options>
                        <router-id operation="delete"></router-id>
                    </routing-options>"""


            commant = "Deleted " + item

            result = upload_input(self, input)

            # End the NETCONF session and close the connection
            dev.close()

            if result == None:
                print(bcolors.OKGREEN + item + " Deleted" + bcolors.ENDC)
 
            else:
                print(bcolors.FAIL + item + "not Deleted" + bcolors.ENDC)  

            return



        # delete protocols

        if item in list_protocols:

            input= """
                    <protocols>
                        <temp operation="delete"></temp>
                    </protocols>"""
            
            input = input.replace("temp", item)

            commant = "Deleted " + item

            result = upload_input(self, input)

            # End the NETCONF session and close the connection
            dev.close()

            if result == None:
                print(bcolors.OKGREEN + item + " Deleted" + bcolors.ENDC)
 
            else:
                print(bcolors.FAIL + item + "not Deleted" + bcolors.ENDC)  

            return 
            


        # NO matches

        print(bcolors.FAIL + item + " not found" + bcolors.ENDC)

        # End the NETCONF session and close the connection
        dev.close()
        