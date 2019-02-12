##  vSporn_Python

This project was made to modify the configuration of all Juniper devices (e.g. router, switches, firewalls) using JUNOS as OS and build complete topologies in VMware automatically.


### Configuration features 

- get current configuration
- update configuration by using a prepared config file
- delete selected parts of the configuration


### Create topology features 

- build complete virtual topologies based on a YMAL-file
- create and configure virtual vMX routers 
- generate all network connections 
  - management connection
  - internal connection between controlPlane and forwardingPlane
  - external connections between virtual routers
- upload a custom default configuration
- each configuration step will be checked for possible errors before the implementation starts 
  - exception handling for different events and adequate dynamic reaction
- every step and every result will be written in the console 

------------
------------
------------

### How to use ?

##### start ```main.py``` 

You will find more examples there

------------
------------
------------

### First Step: Connect to the Juniper device

open ```main.py``` and specify the device you want to connect with in this format:

```
Juniper_MOD("<IP>", "<user>", "<password>", "telnet", "23") 
```

<br/>

------------

#### Example:

```
Juniper_MOD("192.18.10.90", "netconf", "Juniper", "telnet", "23")
```
------------
------------
------------

### Get the current configuration

specify the part of the configuration that you want to have displayed:

- "" (complete configuration)

- hostname | host-name

- router-id | id

- protocol | protocols | ospf | isis | bgp | bfd | mpls | stp | ldp | rsvp | lldp 

- interface | interfaces | ge-0/0/0-9 | lo0 | fxp0

- policy | policies | my-policy-name

- firewall | firewalls

<br/>

------------

#### Example:

```
router_01.GET_conf("")
router_01.GET_conf("firewall")
```
------------
------------
------------

### Update the configuration


upload configuration from an external file

<br/>

------------

#### Example:

```
router_01.set_conf("./my-junos-config.conf")
```
<br/>

##### my-junos-config.conf    
###### default folder: CONFIG

```
    interfaces {

        ge-0/0/0 {
            unit 0 {
                family inet {
                    address 7.43.4.2/24;
                }
            }
        }

        lo0 {
            unit 0 {
                family inet {
                    address 1.1.1.1/32;
                }
            }
        }
    }

    protocols {
        ospf {        
            area 0.0.0.0 {
                interface all;
            }
        }
    }
```

------------
------------
------------

### Delete selected parts of the configuration

specify in quotes and keyword "delete" the part of the configuration that you want to delete:


- delete hostname | delete host-name

- delete router-id | delete id

- delete ge-0/0/0-9 | delete fxp0 | delete lo0

- delete ospf | isis | bgp | bfd | mpls | stp | ldp | rsvp | lldp

- delete "policy-name"

- delete "firewall-role"

<br/>

------------

#### Example:

```
router_01.del_conf("delete ge-0/0/0")
router_01.del_conf("delete ospf")
```

------------
------------
------------
------------
------------

### Create virtual topologies

- build a complete custom topology in VMware by using a YMAL-file

- creates ressouce pool, virtual machines and all network connections

- upload a new configuration automatically on each virtual machines and change the management IPs

- need Juniper vMX templates >>> more informations at the end of this document

<br/>

------------

#### Example:

```
Create_MAIN.Create("./TOPOLOGY/Test_01.yml")
```

- the configuration settings of your VMware environment (vcenter_ip, username, password...) are in the connection section of the YMAL-file

- all names of the new topology will be automatically generated and got the chosen project_name as prefix

<br/>

##### test_topology.yaml 
###### default folder: TOPOLOGY

```
project_name: Test_01

connection:                          # VMware configuration

    vcenter_ip:    
    username:      
    password:      
    host_name:     
    data_center:   
    datastore:     
    vm_folder:     

default_settings_TEMPLATE:

    template_mgmt_IP:   "192.18.10.100"
    default_username:   "netconf"
    default_password:   "Netconf"
    external_interface: "external_network"

devices:                             # router list

    - name: R01                      # router name
      type: vMX
      version: 18.2R1.9          
      mgmt_ip: 192.18.10.101/24      # new management IP
      mgmt_ip_gw: 192.18.10.1        # gateway
      network: 
          - R01-R03                  # network connection between router R01 and router R03 (interface ge-0/0/0)
          - R01-R02                  # network connection between router R01 and router R02 (interface ge-0/0/1)

    - name: R02
      type: vMX
      version: 18.2R1.9
      mgmt_ip: 192.18.10.102/24
      mgmt_ip_gw: 192.18.10.1 
      network: 
          - R02-R03
          - R01-R02

    - name: R03
      type: vMX
      version: 18.2R1.9
      mgmt_ip: 192.18.10.103/24
      mgmt_ip_gw: 192.18.10.1 
      network: 
          - R01-R03
          - R02-R03
```

------------

#### Create Juniper vMX templates 


- template VMs are created by using Juniper OVA-files (https://support.juniper.net/support/downloads/?p=vmxeval#sw)

- created VMs have a default name setting as following:
  - controlPlane: "TEMPLATE_vCP_" + version
  - forwardingPlane: "TEMPLATE_vFPC_" + version 

- delete all network connections on both machines 

- VM configuration of the forwardingPlane has to be changed to 3 CPU-cores and 3 GB RAM

- the VM of the controlPlane needs a default configuration with an user, access permissions and management IP

- a management IP is necessary to upload the initial configuration 
  - temporary management IP in this example: 192.18.10.100/24  
  
<br/>

##### template.conf
###### folder: CONFIG

```
system {
    login {
        user netconf {
            uid 2001;
            class super-user;
            authentication {
                encryted-password "" 
            }
        }
    }
    host-name TEMPLATE;
    services {
        ssh {
            root-login allow;
        }
        telnet {
            connection-limit 5;
        }
        netconf {
            ssh;
        }
    }
}

interfaces {
    fxp0 {
        unit 0 {
            family inet {
                address 192.18.10.100/24;
            }
        }
    }
}

routing-options {
    static {
        route 0.0.0.0/0 next-hop 192.18.10.1;
    }
}
```
