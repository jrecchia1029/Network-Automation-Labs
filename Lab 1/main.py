from netmiko import ConnectHandler
import re


def get_interface_ip(connection, iface):
    # Write out the command substituting the interface name where appropriate
    cmd = "show ip interface {} | i Internet address".format(iface)
    interface_info = connection.send_command(cmd)
    # Trim leading/trailing whitespace
    interface_info = interface_info.strip()
    # Use regex to obtain the ip address from the output of the above command
    ip_address_re = r'Internet address is (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\/\d+'
    match = re.match(ip_address_re, interface_info)
    if match:
        return match.group(1)  # return the first group of the regex
    else:
        return None


def configure_ospf(connection, interface_ip):
    # Check if connection is config mode
    if connection.check_config_mode() == False:
        connection.config_mode()
    # Start ospf process
    # Note: use send_command_timing whenever the router prompt changes
    connection.send_command_timing("router ospf 1")
    # Advertise the interface
    cmd = "network {} 255.255.255.255 area 0".format(interface_ip)
    connection.send_command(cmd)
    # Exit config mode
    connection.exit_config_mode()


def verify_ospf_config(connection):
    # Print out OSPF section of running-config
    output = connection.send_command_timing("show running-config | s ospf")
    print("OSPF Config\n-------------------------------")
    print(output)
    print("-------------------------------")


def advertise_ospf_interface(device_config):
    # Create connection
    connection = ConnectHandler(**device_config)
    # Enter enable mode
    connection.enable()
    # Get ip address of an interface
    interface_ip = get_interface_ip(connection, 'Gi0/1')
    print("We will be advertising {} on {}".format(interface_ip, device_config["ip"]))
    # Start ospf and advertise interface
    configure_ospf(connection, interface_ip)
    print("Configured OSPF on {}".format(device_config["ip"]))
    # Verify config
    verify_ospf_config(connection)
    # Close the connection
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


if __name__ == "__main__":
    main()
