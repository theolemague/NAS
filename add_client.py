from os import system 
import json


def get_pe(config):
    routers = config["routers"]
    list_pe = []
    for r in routers:
        if "PE" in r["name"]:
            list_pe.append(r)

    print("Backbone PE are :")
    names = []
    pe = ""
    for r in list_pe :
        print(r["name"])
        names.append(r["name"])
    while True :
        pe=input("Select the PE :")
        if pe in names : 
            break
        else:
            print("Error in the name of the selected pe") 
    i_pe = 0
    for i in range(len(routers)) :
        if routers[i]["name"] == pe :
            i_pe = i
    return i_pe

def get_interface(pe):
    available_int = []
    names = []
    print("Interfaces available on the router", pe["name"])
    for i in range(len(pe["interface"])):
        interface = pe["interface"][i]
        if interface["name"]!="Loopback0" and interface["name"]!="GigabitEthernet1/0":
            if "available" in interface :
                if interface["available"]:
                    available_int.append(interface)
                    names.append(interface["name"][0]+interface["name"][-3:])
                    print("\t",interface["name"], "ip :", interface["address"])
            else:
                available_int.append(interface)
                names.append(interface["name"][0]+interface["name"][-3:])
                print("\t", interface["name"], "ip :", interface["address"])
    
    inter = ""
    while True :
        inter=input("Select the interface (short not accepted) \n")
        inter = inter[0]+inter[-3:] 
        if inter in names :
            break
        else:
            print("Error in the name of the selected interface") 
    
    i_int = 0
    for i in range(len(pe["interface"])) :
        name = pe["interface"][i]["name"]
        if inter[0] == name[0] and inter[-3:] == name[-3:]:
            i_int = i

    return i_int


def add_vrf(config, i_pe, i_int, ospf):
    pe = config["routers"][i_pe]
    interface = pe["interface"][i_int]
    print("Adding a VRF on interface ", interface["name"])
    addr=interface["address"].split(".")
    addr[3]=str(int(addr[3])+1)
    addr='.'.join(addr)
 
    vrf_id=input("Enter the vrf id :")
    # bgp_as=input("Enter the bgp AS id :")

    rd = 1
    rt = 100

    # neighbors=[]
    # if "neighbor" in pe["bgp"]:
    #     neighbors=config["routers"][i_pe]["bgp"]["neighbor"]
    # else:
    #     config["routers"][i_pe]["bgp"]["neighbor"]= neighbors
    # neighbor={
    #     "address":addr,
    #     "as":bgp_as}
    # config["routers"][i_pe]["bgp"]["neighbor"].append(neighbor)

    for r in config["routers"]:
        if "vrf" in r:
            for vrf in r["vrf"]:
                max_rd=0
                max_rt = 0
                if vrf["id"] == vrf_id:
                    rd=int(vrf["rd"].split(":")[0])
                    rt=int(vrf["route-target import"].split(":")[0])
                    break
                else:
                    max_rd=int(vrf["rd"].split(":")[0])+1
                    max_rt = int(vrf["route-target import"].split(":")[0])+100
                    rd = max_rd
                    rt = max_rt

    vrf={
        "id": vrf_id,
        "interface":interface["name"],
        "rd":str(rd)+":"+str(rd),
        "route-target import": str(rt)+":"+str(rt),
        "route-target export": str(rt)+":"+str(rt),
        "ospf":ospf,
        # "bgp":bgp_as,
        "address":addr
    }

    config["routers"][i_pe]["vrf"].append(vrf)
    print("VRF created")
    return addr

def add_ce(config, addr):
    res=input("Does the CE need to be configured ?(y/n) :")
    if "n" in res :
        return
    
    name=input("Enter the name of the CE : ")
    addr_client=input("Enter the ip address of the client network <ip> <mask> : ")
    ip_addr = addr_client.split(" ")[0]
    mask_addr = addr_client.split(" ")[1]
    ospf=input("Enter the ospf id :")
    ce={
        "name":name,
        "interface":[
            {
                "name" : "GigabitEthernet1/0",
                "address" : addr,
                "mask" : "255.255.255.252"
            },
            {
                "name" : "GigabitEthernet2/0",
                "address" : ip_addr,
                "mask" : mask_addr
            }
        ],
        "ospf" : {
            "id" : ospf,       
            "area" : "0"
        }
    }

    config["routers"].append(ce)
    config["port"][name] = ""
    



def add_client(config):
    routers = config["routers"]
    i_pe = 0
    i_int = 0
    while True:
        i_pe = get_pe(config)
        pe = routers[i_pe]
        
        opsf_count = "0"
        if "vrf" in pe:
            for vrf in pe["vrf"]:
                if int(opsf_count) < int(vrf["ospf"]) :
                    opsf_count=vrf["ospf"]
        else:
            opsf_count=pe["ospf"]["id"]
            config["routers"][i_pe]["vrf"] = []
        
        i_int = get_interface(pe)

        config["routers"][i_pe]["interface"][i_int]["available"]=False

        ce_addr = add_vrf(config, i_pe, i_int,str(int(opsf_count)+1))
        add_ce(config, ce_addr)
    
        ans=input("Do you want to add another CE ? (y/n) : ")
        if "n" in ans:
            break 
    return config

if __name__ == "__main__":
    with open('config.json','r') as f:
        config = json.load(f)  
    config = add_client(config)
    with open('config.json','w') as f:
        json.dump(config,f,indent=2)

