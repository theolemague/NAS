import json
import telnetlib
import sys
import time

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

def set_neighbor_address(hostname, networks, tn):
    global routers
    for router in routers :
        if router["name"] == hostname :
            for inter in router["interfaces"]:
                if find_newtwork(inter) in networks :
                    tn.write(bytes("neighbor "+inter["address"]+" remote-as "+router["bgp"]["as"]+"\r",'utf-8'))

def set_neighbor_loopback_address(hostname, tn):
    global routers
    for router in routers :
        if router["name"] == hostname :
            for inter in router["interfaces"]:
                if inter["name"] == "Loopback0":
                    tn.write(bytes("neighbor "+inter["address"]+" remote-as "+router["bgp"]["as"]+"\r",'utf-8'))
                    tn.write(bytes("neighbor "+inter["address"]+" update-source loopback 0\r",'utf-8'))

def clear_interface(tn):
    tn.write(b"no ip address \r")
    tn.write(b"shutdown\r")
    tn.write(b"no mpls ip\r")
    tn.write(b"no mpls mtu\r")

def config_interfaces(router, tn):
    for inter in router["interfaces"]:
        tn.write(bytes("interface "+inter["name"]+"\r",'utf-8'))
        tn.write(bytes("ip address "+inter["address"]+" "+inter["mask"]+"\r", "utf-8"))
        tn.write(b"no shutdown\r")
        if inter["name"] != "Loopback0" and inter["mpls"]:
            tn.write(b"mpls ip\r") 
            tn.write(bytes("mpls mtu "+router["mpls"]["mtu"]+"\r", "utf-8"))
        tn.write(b"exit\r")

def clear_mpls(tn):
    tn.write(b"no mpls ldp router-id Loopback0\r")
    tn.write(b"no mpls label range\r")

def config_mpls(router, tn):
    mpls = router["mpls"]
    tn.write(b"ip cef\r")
    tn.write(b"mpls ldp router-id Loopback0\r")
    if "min_label" in mpls:
        tn.write(bytes("mpls label range "+mpls["min_label"]+" "+mpls["max_label"]+"\r",'utf-8'))

def clear_bgp(tn):
    tn.write(b'do sh ip bgp summary\r')
    res = tn.read_until(b"local AS number", 0.1).decode('ascii')
    if "local AS number" in res :
        bgp_as = int(tn.read_until(b"\n").decode('ascii'))
        tn.write(bytes("no router bgp "+str(bgp_as)+"\r",'utf-8'))

def config_bgp(router, tn):
    bgp = router["bgp"]
    tn.write(bytes("router bgp "+bgp["as"]+"\r",'utf-8'))
    if "neighbor" in bgp:
        networks = []
        for inter in router["interfaces"]:
            networks.append(find_newtwork(inter))
        for neighbor in bgp["neighbor"]:
            set_neighbor_address(neighbor, networks, tn)
    # config iBGP
    if "ibgp" in bgp:
        neighbors = bgp["ibgp"]
        for n in neighbors:
            set_neighbor_loopback_address(n, tn)
    tn.write(b"exit\r")

def clear_ospf(tn):
    tn.write(b'do sh ip ospf summary-address\r')
    tn.read_until(b"sh ip ospf summary-address").decode('ascii')
    res = tn.read_until(b"#", 0.1).decode('ascii')
    if "Process" in res :
        res = res.split(" ")
        for i in range(len(res)) :
            if res[i] == "Process":
                tn.write(bytes("no router ospf "+res[i+1].split(",")[0]+"\r",'utf-8'))

def config_ospf(router, tn):
    ospf = router["ospf"]
    tn.write(bytes("router ospf "+ospf["id"]+"\r",'utf-8'))
    for inter in router["interfaces"]:
        if inter["name"] != "Loopback0" :
            addr = find_newtwork(inter)
            r_mask = inverse_Mask(inter)
            tn.write(bytes("network "+addr+" "+r_mask+" area "+ospf["area"]+"\r",'utf-8'))
        elif "ibgp" in router["bgp"] :
            tn.write(bytes("network "+inter["address"]+" 0.0.0.0 area "+ospf["area"]+"\r",'utf-8'))
    tn.write(b"exit\r")


def clear_vrf(tn, vrf):
    tn.write(b'do sh ip vrf detail\r')
    test = tn.read_until(b"sh ip vrf detail").decode('ascii')
    res = tn.read_until(b"#", 0.1).decode('ascii')
    if "VRF" in res :
        res = res.split(" ")
        for i in range(len(res)) :
            if '\nVRF' in res[i]:
                vrf_used = res[i+1].split(";")[0]
                if vrf_used not in vrf :
                    tn.write(bytes("no ip vrf "+res[i+1].split(";")[0]+"\r",'utf-8'))
  

def config_vrf(router, tn):

    for vrf in router["vrf"]:
        interface = 0
        for inter in router["interfaces"]:
            if inter["name"] == vrf["interface"] :
                interface = inter
        
        #create vrf TODO est ce que le rd c'est bien ca ou non je ne sais pas c'est la galère
        tn.write(bytes("ip vrf "+vrf["id"]+"\r",'utf-8'))
        tn.write(bytes("rd "+vrf["rd"]+":100\r",'utf-8'))
        tn.write(bytes("route-target export "+router["bgp"]["as"]+":100\r",'utf-8'))
        tn.write(bytes("route-target import "+router["bgp"]["as"]+":100\r",'utf-8'))
        tn.write(b"exit\r")
        
        #config interface
        tn.write(bytes("interface "+interface["name"]+"\r",'utf-8'))
        tn.write(bytes("ip vrf forwarding "+vrf["id"]+"\r",'utf-8'))            
        tn.write(b"exit\r")

        # config opsf TODO pareil entre rd et as
        if "ospf" in vrf :
            tn.write(bytes("router ospf "+vrf["ospf"]+" vrf "+vrf["id"]+"\r",'utf-8'))
            tn.write(bytes("redistribute bgp "+router["bgp"]["as"]+" subnets\r",'utf-8'))
            addr = find_newtwork(interface)
            r_mask = inverse_Mask(interface)
            tn.write(bytes("network "+addr+" "+r_mask+" area "+router["ospf"]["area"]+"\r",'utf-8'))
            tn.write(b"exit\r")


def config_router(port, router):

    tn = telnetlib.Telnet("localhost", port)
    tn.write(b'\ren\r')
    
    tn.write(b'conf t\r')   
    tn.write(bytes("hostname "+router["name"]+"\r",'utf-8'))

    # Config interface
    clear_interface(tn)
    config_interfaces(router, tn)

    # Config OSPF
    if "ospf" in router:
        clear_ospf(tn)
        config_ospf(router, tn)

    # (conf) MPLS
    if "mpls" in router:
        clear_mpls(tn)
        config_mpls(router, tn)

    # (conf) BGP
    if "bgp" in router:
        clear_bgp(tn)
        config_bgp(router, tn)

    # Config VRF
    if "vrf" in router:
        vrf_id = []
        for v in router["vrf"]:
            vrf_id.append(v["id"])
        clear_vrf(tn, vrf_id)
        config_vrf(router, tn)

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
    if len(sys.argv) <=1 : 
        print("Missing arg !")
    
    for r in routers :
        if sys.argv[1] == "all" :
            config_router(r["port"], r)
        
        if sys.argv[1] == "update" :
            config_router(r["port"], r)