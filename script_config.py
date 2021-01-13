import json
import telnetlib
import sys

def clean_router(port,router):
    tn = telnetlib.Telnet("localhost", port)
    tn.write(b'\ren\r')
    tn.write(b'\rconf t\r')
    for inter in router["interfaces"]:
        tn.write(bytes("interface "+inter["name"]+"\r",'utf-8'))
        tn.write(b"no ip address \r")
        tn.write(b"shutdown\r")
        tn.write(b"no mpls ip\r")
        tn.write(b"no mpls mtu\r")
        tn.write(b"exit\r")
    
    tn.write(bytes("no router ospf "+router["ospf"]["id"]+"\r",'utf-8'))
    tn.write(b"no mpls ldp router-id Loopback0\r")
    tn.write(b"no mpls label range\r")
    
    tn.write(b"end\r")
    tn.write(b"write\r")
    tn.write(b"reload\r\r")
    
    print("Clean for", router["name"], port)



def find_newtwork(inter):
        cont=0
        addr=""
        y = inter["address"].split(".")
        x = inter["mask"].split(".")
        for elt in x:
            cont+=bin(int(elt)).count("1") #find the /32 etc 
        if cont <9:
            addr=str(int(x[0])&int(y[0]))+".0.0.0"
        elif cont < 17:
            addr=y[0]+"."+str(int(x[1])&int(y[1]))+".0.0"
        elif cont<25:
            addr=y[0]+"."+y[1]+"."+str(int(x[2])&int(y[2]))+".0"
        else :
            addr=y[0]+"."+y[1]+"."+y[2]+"."+str(int(x[3])&int(y[3]))
        return addr

def inverse_Mask(inter):
    invert=""
    cont=0
    x = inter["mask"].split(".")
    for elt in x:
        cont+=bin(int(elt)).count("1")
    if cont <9:
        test=255-int(x[0])
        invert=str(test)+".255.255.255"
    elif cont < 17:
        test=255-int(x[1])
        invert="0."+str(test)+".255.255"
    elif cont<25:
        test=255-int(x[2])
        invert="0.0."+str(test)+".255"
    else :
        test=255-int(x[3])
        invert="0.0.0."+str(test)
    return(invert)





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
        # for network in ospf["networks"]:
        for inter in router["interfaces"]:
            if inter["name"] != "Loopback0" :
                addr = find_newtwork(inter)
                r_mask = inverse_Mask(inter)
                tn.write(bytes("network "+addr+" "+r_mask+" area "+ospf["area"]+"\r",'utf-8'))

    # (conf) MPLS
    if "mpls" in router:
        mpls = router["mpls"]
        tn.write(b"ip cef\r")
        tn.write(b"mpls ldp router-id Loopback0\r")
        if "min_label" in mpls:
            tn.write(bytes("mpls label range "+mpls["min_label"]+" "+mpls["max_label"]+"\r",'utf-8'))

    
    tn.write(b"end\r")
    tn.write(b'write\r')
    print("Done for", router["name"])


def config_vpc(port, vpc):

    tn = telnetlib.Telnet("localhost", port)
    tn.write(bytes("ip "+vpc["address"]+"/"+vpc["mask"]+" "+vpc["gateway"]+"\r",'utf-8'))
    print("Done for", vpc["name"])



if __name__ == "__main__":

    config = 0
    with open('config.json','r') as f:
        config = json.load(f)
    routers = config["routers"]
    vpcs = config["vpcs"]
    for r in routers :
        if len(sys.argv) >1 and sys.argv[1] == "clean" :
            clean_router(r["port"], r)
        else :
            config_router(r["port"], r)
    for pc in vpcs :
        config_vpc(pc["port"], pc)
