import getpass
import telnetlib
import json




def router_configurator(name,host,router_id,interfaces):
    HOST = host
    user = input("Enter your "+name+" telnet username: ")
    password = getpass.getpass()

    tn = telnetlib.Telnet(HOST)

    tn.read_until(b"Username: ")
    tn.write(user.encode('ascii') + b"\n")
    if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")


    tn.write(b"enable\n")
    tn.write(b"cisco\n")
    tn.write(b"conf ter\n")
    tn.write(b"ipv6 unicast-routing\n")
    tn.write(b"ipv6 router ospf 1\n")
    tn.write(bytes("router-id "+router_id+"\n", 'utf-8'))
    tn.write(b"end\n")

    for i in range(len(interfaces)):
        tn.write(b"conf ter\n")
        tn.write(bytes("interface "+interfaces[i]["name"]+"\n",'utf-8'))
        tn.write(b"no shut\n")
        tn.write(bytes("ipv6 add "+interfaces[i]["ip6"]+"\n",'utf-8'))
        tn.write(bytes("ipv6 ospf 1 area "+interfaces[i]["area"]+"\n",'utf-8'))
        tn.write(b"end\n")

    
    tn.write(b"exit\n")
    tn_read =  tn.read_very_eager()
    print(tn_read)

    print(tn.read_all().decode('ascii'))

    print(1)


with open('config_scheme.json') as file:
    data = json.load(file)

for i in data["Routers"]:
    host_ = data["Routers"][str(i)]["HOST"]
    name_ = i
    router_id_ = data["Routers"][str(i)]["router_id"]
    interfaces_ = data["Routers"][str(i)]["Interfaces"] 
    
    router_configurator(name_,host_,router_id_,interfaces_)

for i in range(1,len(data["Routers"])+1):
    print(i)
print(str(len(data["Routers"]))+"R")
print(data["Routers"]["R1"]["Interfaces"][0])