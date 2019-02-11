from MOD.Juniper_MOD import Juniper_MOD
from CREATE.Create_MAIN import Create_MAIN

#----------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------- main -------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

class Main:

    def main():

        router_01 = Juniper_MOD("172.18.10.85", "netconf", "Netconf", "telnet", "23")

        router_01.GET_conf("")

        #router_01.SET_conf("./CONFIG/STP_R1.conf")

        #router_01.DEL_conf("delete filter_s_tcp")

        #Create_MAIN.Create("./TOPOLOGY/test.yml")


        


        """
        GET_CONF

            Complete Configuration 
                >>> ""

            Host-Name 
                >>> "hostname" "host-name"

            Router-ID 
                >>> "router-id" "id" "ID"

            Protocols
                >>> "protocols" "protocol" 

            Specific Protocol (e.g. OSPF) 
                >>> "ospf" "OSPF" 

            Policys
                >>> "policys" "policy"

            Firewalls
                >>> "firewall" "firewalls"

            Interfaces
                >>> "interfaces" "interface"

            Specific Interface (e.g. ge-0/0/0) 
                >>> "ge-0/0/0"  


        SET_CONF

            >>> insert path to conf_file
        

        DEL_CONF

            Delete Interface (e.g. ge-0/0/0) 
                >>> "delete ge-0/0/0"

            Delete Host-Name
                >>> "delete hostname" "delete host-name"

            Delete Router-ID 
                >>> "delete router-id" "delete id" 

            Delete Protocol (e.g. OSPF) 
                >>> "delete ospf" "delete OSPF" 

            Delete Policy (e.g. test-pol)
                >>> "delete test-pol" 

            Delete Firewall (e.g. filter_test) 
                >>> "delete filter_test" 

        """



    if __name__ == "__main__":
        main()



