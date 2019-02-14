from netmiko import ConnectHandler
import re

def get_interface_ip(connection, iface):
    #Write out the command substituting the interface name where appropriate
    cmd = "show ip interface {} | i Internet address".format(iface)
    interface_info = connection.send_command(cmd)
    #Trim leading/trailing whitespace
    interface_info = interface_info.strip()
    #Use regex to obtain the ip address from the output of the above command
    ip_address_re = r'Internet address is (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\/\d+'
    match = re.match(ip_address_re, interface_info)
    if match:
        return match.group(1) #return the first group of the regex
    else:
        return None

def configure_ospf(connection, interface_ip):
    #Check if connection is config mode
    if connection.check_config_mode() == False:
        connection.config_mode()
    #Start ospf process
    connection.send_command_timing("router ospf 1") #Note: use send_command_timing whenever the router prompt changes
    #Advertise the interface
    cmd = "network {} 255.255.255.255 area 0".format(interface_ip)
    connection.send_command(cmd)
    #Exit config mode
    connection.exit_config_mode()

def advertise_ospf_interface(device_config):
    #Create connection
    connection = ConnectHandler(**device_config)
    #Enter enable mode
    connection.enable()
    #Get ip address of an interface
    interface_ip = get_interface_ip(connection, 'Gi0/1')
    #Start ospf and advertise interface
    configure_ospf(connection, interface_ip)
    #Close the connection
    connection.disconnect()

device1_config = {
    "device_type": "cisco_ios",
    "ip": "192.168.18.143",
    "username": "jrecchia",
    "password": "password",
    "secret": "password"
}
device2_config = {
    "device_type": "cisco_ios",
    "ip": "192.168.18.142",
    "username": "jrecchia",
    "password": "password",
    "secret": "password"
}

def main():
    routers = []
    routers.append(device1_config)
    routers.append(device2_config)

    for rtr in routers:
        advertise_ospf_interface(rtr)
        print("Configured {}".format(rtr["ip"]))

if __name__ == "__main__":
    main()