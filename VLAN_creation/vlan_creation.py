import getpass
import time
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException

print("\n" + "-----" * 10)
print("\n[+] Hello, I hope you have a good day...")
time.sleep(0.5)

# The code is opening up the login.txt file. In this file, we have the log-in credentials for the SSH connections
# The code is checking whether the username introduced by the user is available in the login.txt file;

# STEP NO. 1 (SEE DIAGRAM ATTACHED)

while True:
    user = input("\n[+] Please enter your username: ")
    password = getpass.getpass()

    with open("login.txt") as f:
        file_output = f.read()
        file_output = file_output.splitlines()
        clients_list = []
        password_list = []
        for element in file_output:
            element = element.split()
            user2 = element[1]
            password1 = element[3]
            clients_list.append(user2)
            password_list.append(password1)
        if user in clients_list and password in password_list:
            break
        else:
            print("\n[-] Wrong username/password combination, please try again.")

# ----------------------------------------------------------------------------------------------------------

# This part of the code deals with the authorization issues depicted in the diagram. I tried to mimic a production
# environment where other instances are accessed in order to determine the authorization level a user has.
# I will amend this code in the future to perform an authorization process as close as possible to the production
# environment. The files that are being handled here are text files.

# STEP NO. 2 (SEE DIAGRAM ATTACHED)

with open("devices.txt") as d:
    output = d.read()
    output = output.splitlines()
    all_devices = []
    for item in output:
        item = item.split()
        device = item[1]
        all_devices.append(device)

with open("authorization.txt") as e:
    output1 = e.read()
    output1 = output1.splitlines()

for item1 in output1:
    if user in item1:
        item1 = item1.split()
        break

while True:
    choice1 = input("\n[+] Would you like to configure multiple devices at once? (y/n): ")
    allowed = []

    if choice1 == "n":
        while True:
            choice2 = input("\n[+] Please specify the IP of the device you want to configure: ")
            allowed.append(choice2)
            if choice2 not in item1:
                print("\n[-] !!! You are not authorized to access this device !!!")
            else:
                break
        break

    elif choice1 == "y":
        while True:
            choice3 = input("\n[+] Please specify how many devices you want to configure: ")
            if not choice3.isdigit():
                print("\n[-] Please specify a number...")
                continue
            else:
                break

        choice3 = int(choice3)
        devices_list = []

        for n in range(1, choice3 + 1):
            x = input("\n[+] Please enter the IP of switch number {}: ".format(n))
            x = x.strip()

            devices_list.append(x)

        not_allowed = []

        for device2 in devices_list:
            if device2 in item1:
                allowed.append(device2)
                pass
            else:
                not_allowed.append(device2)

        if len(not_allowed) == 0:
            pass
        else:
            print("\n[-] You are not authorized to access the following devices:\n ")
            for yy in not_allowed:
                print("    [-] " + yy + "; ")
            print("\n[-] Resuming process with the rest of switches to which you have access...\n")
        break

    else:
        print("\n[-] Please use either y or n. ")

# ----------------------------------------------------------------------------------------------------------

# The user is asked for the VLAN configuration options: VLAN ID and name. I created from these a dictionary
# that is appended to a list. The list is accessed below, in STEP NO 5.

# STEP NO. 3 (SEE DIAGRAM ATTACHED)

while True:
    option4 = input("\n[+] Specify the number of VLANs you want to configure: ")
    if not option4.isdigit():
        print("\n[-] Please input a number...")
    else:
        break
option4 = int(option4)

values = []
for p in range(1, option4 + 1):
    my_values = {}
    name = input("\n[+] Please specify the NAME of VLAN {}: ".format(p))
    name = name.upper()
    while True:
        ids = input("[+] Please specify the ID of VLAN {}: ".format(p))
        if ids.isdigit():
            break
        else:
            print("\n[-] Please input a number.")
    my_values["vlan"] = name
    my_values["ids"] = ids
    values.append(my_values)


# ----------------------------------------------------------------------------------------------------------
# This function contains the commands that are executed on the switch once the SSH connection is established.
# It is the part of the code that actually performs actions on the switch itself. It checks whether there are
# existing VLAN IDs/names. If it finds that the VLAN ID/name introduced by the user is already used,
# the code skips the commands for that specific VLAN and logs the error. At the end of the code, the user will be
# greeted with a list of switches that already had the specified VLAN IDs/names configured. The user has then to
# manually do his own research in this regard.

# STEP NO. 5

def switch_commands():
    while True:
        try:
            global unconfigured_switches

            def config_backup_vlan_backup(ip1):
                print("\n\n[+] Successfully connected to device: {} \n[+] Creating a backup of the running configuration and "
                      "for the VLAN configuration of the device, "
                      "please wait. ".format(ip1))
                sh_run = net_connect.send_command('show run')
                saveoutput = open("switch" + ip1, "w")
                saveoutput.write(sh_run)

                sh_vlan = net_connect.send_command('sh vlan brief')
                saveoutput2 = open('switch_vlan' + ip1, 'w')
                saveoutput2.write(sh_vlan)

                print("\n\n[+] A backup is in place :).")
                time.sleep(1.5)

            def vlan_id_name_check():
                output5 = net_connect.send_command("sh vlan brief")
                output5 = output5.splitlines()
                configured_ids = []
                configured_vlans = []

                for elements in output5:
                    elements = elements.strip().split()
                    for elements2 in elements:
                        if elements2[0].isdigit():
                            configured_ids.append(elements[0])
                            configured_vlans.append(elements[1])

                existing_vlan_ids = []
                existing_vlan_names = []

                for dictionary2 in values:
                    for vlan_ids in configured_ids:
                        number1 = int(vlan_ids)
                        number = int(dictionary2["ids"])
                        if number == number1:
                            existing_vlan_ids.append(number)
                    for vlan_names in configured_vlans:
                        vlan_names = vlan_names.upper()
                        if vlan_names == dictionary2["vlan"]:
                            existing_vlan_names.append(vlan_names)

                return existing_vlan_ids, existing_vlan_names

            net_connect = ConnectHandler(**sw)
            time.sleep(0.5)
            net_connect.enable()
            config_backup_vlan_backup(ip)
            function = vlan_id_name_check()

            vlan_ids_for_print = function[0]
            vlan_names_for_print = function[1]

            z = 0
            if len(vlan_ids_for_print) != 0:
                print("\n[-] The following VLAN IDs are already configured on the switch: ")
                z += 1
                for idss in vlan_ids_for_print:
                    print("* " + str(idss) + "; ")
                time.sleep(1.5)
            else:
                pass

            if len(vlan_names_for_print) != 0:
                print("\n[-] The following VLAN names are already configured on the switch: ")
                z += 1
                for names in vlan_names_for_print:
                    print("* " + names + "; ")
                time.sleep(1.5)
            else:
                pass

            if z != 0:
                print("\n[-] Skipping the overlapping configuration for this specific switch, as there is an overlap "
                      "between "
                      "the user's "
                      "input and the configured VLAN names/IDs...")
                unconfigured_switches.append(ip)
                time.sleep(2)

            else:
                for dictionary in values:
                    if dictionary["ids"] in vlan_ids_for_print or dictionary['vlan'] in vlan_names_for_print:
                        pass
                    else:
                        net_connect.send_config_set(['vlan ' + dictionary["ids"], 'name ' + dictionary["vlan"]])
                print("\n[+] Configuration successfully implemented. ")
                print("\n\t\t!!!!!!! CONFIGURATION FOR SWITCH {} !!!!!!!".format(ip))
                output4 = net_connect.send_command("sh vlan brief")
                print(output4)
                print("\n------------------------------------------------------\n\n\n\n")

            time.sleep(1.5)
            break

        except ValueError:
            pass


# ----------------------------------------------------------------------------------------------------------

# Here, the script goes through the list of IPs the user introduced previously. It attempts an SSH connection.
# If the SSH connection is unsuccessful, it prints an error. If it is successful, then the code goes ahead and
# executes the commands listed in the switch_commands function.

# STEP NO. 4

failed_connections = []
unconfigured_switches = []

for ip in allowed:
    xyz = 0
    while xyz == 0:
        try:
            print("\n[+] Attempting connection to device {}, please wait.... ".format(ip))
            sw = {'device_type': "cisco_ios",
                  'host': ip,
                  'username': user,
                  'password': password,
                  'secret': password
                  }
            switch_commands()
            xyz += 1

        except NetMikoTimeoutException:
            print("\n[-] !!! Connection to device {} failed... !!!".format(ip))
            time.sleep(0.5)
            reload = input("\n[-] Would you like to retry the connection? (y/n): ")
            if reload == "y":
                pass
            elif reload == "n":
                failed_connections.append(ip)
                break


print("\n\n\n\t !!!! ------ SCRIPT FINISHED ------ !!!!\n\n")

if len(failed_connections) != 0:
    print("\n\n[-] Could not establish an SSH connection to the following devices: ")
    for connection in failed_connections:
        print("* " + connection)

elif len(unconfigured_switches) != 0:
    print("\n\n[-] The following switches were not configured due to an overlap of names/IDs: ")
    for switch in unconfigured_switches:
        print("* " + switch)
    print("\n\n")

else:
    print("\n\n[+] No error encountered during configuration....\n[+] Goodbye!")
