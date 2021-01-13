import json
import telnetlib

def config_router(port, router):

    tn = telnetlib.Telnet("localhost", port)
    tn.write(b'\ren\r')

    tn.write(b'conf t\r')
    tn.write(bytes("hostname "+router["name"]+"\r",'utf-8'))
    
    # (conf-if) inter
    for inter in router["interfaces"]:
        tn.write(bytes("interface "+inter["name"]+"\r",'utf-8'))
        tn.write(bytes("ip address "+inter["address"]+" "+inter["mask"]+"\r", "utf-8"))
        tn.write(b"no shutdown\r")
        if inter["name"] != "Loopback0" and inter["mpls"]:
            tn.write(b"mpls ip\r") 
            tn.write(bytes("mpls mtu "+router["mpls"]["mtu"]+"\r",'utf-8'))
        tn.write(b"exit\r")
    
    #(conf) OSPF
    if "ospf" in router:
        ospf = router["ospf"]
        tn.write(bytes("router ospf "+ospf["id"]+"\r",'utf-8'))
        for network in ospf["networks"]:
        # for inter in router["interfaces"]:
            tn.write(bytes("network "+network["address"]+" "+network["mask"]+" area "+network["area"]+"\r",'utf-8'))

    # (conf) MPLS
    if router["mpls"]:
        mpls = router["mpls"]
        tn.write(b"ip cef\r")
        tn.write(b"mpls ldp router-id Loopback0\r")
        if "min_label" in mpls:
            tn.write(bytes("mpls label range "+mpls["min_label"]+" "+mpls["max_label"]+"\r",'utf-8'))

    
    tn.write(b"end\r")
    tn.write(b'write\r')
    print("Done for", router["name"])


if __name__ == "__main__":

    config = 0
    with open('config.json','r') as f:
        config = json.load(f)
    routers = config["routers"]
    for router in routers :
        config_router(router["port"], router)
        