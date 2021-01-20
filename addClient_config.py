from os import system 
import json

def Adding_client():
    with open('config.json','r') as f:
        config = json.load(f)
    flag=1
    liste_PE=[]
    routers = config["routers"]
    for r in routers:
        if (len(r["name"])==3):
            liste_PE.append(r["name"])

    
    while(flag):
        ans=input("\nDo you want to add a client router (CE) on your network ? y/n : ")
        
        if(ans=="y"):
            system('clear')
            print(liste_PE)
            where=input("\n On which PE do you want to add a VRF ? :")
            intDispo=[]
            ospfc=""
            vrfs=[]
            c=0
            for r in config["routers"] :
                c+=1
                if(r["name"]==where):
                    if("vrf" in r):
                        vrft=r["vrf"]
                        vrfs=vrft
                        for vrf in vrft:
                            ospfc=vrf["ospf"]
                    else:
                        ospfc=r["ospf"]["id"]
                        vrfs=[]
                        config["routers"][c-1]["vrf"]=vrfs
                    interfaces=r["interface"]
                    a=0
                    system('clear')
                    print("\n Interfaces available on the router",where,"\n")
                    for inte in interfaces:
                        a+=1
                        if(inte["name"]!="Loopback0" and inte["name"]!="GigabitEthernet1/0"):
                            if("avaible" in inte):
                                if(inte["avaible"]=="yes" or inte["avaible"]=="" ):
                                    intDispo.append(inte)
                                    print("\n")
                                    print(inte)
                            else:
                                config["routers"][c-1]["interface"][a-1]["avaible"]=""
                                intDispo.append(inte)
                                print(config["routers"][c-1]["interface"][a-1])
                                print("\n")
                    
                    inter=input(" Wich interface ? (long/short accepted) \n")
                    if(inter=="GE2/0" or inter == "GigabitEthernet2/0"):
                        for inte in interfaces:
                            if(inte["name"]=="GigabitEthernet2/0"):
                                config["routers"][c-1]["interface"][2]["avaible"]="no"
                                system('clear')
                                print("Adding a VRF on interface ", inte["name"], "of the router", where)
                                idc=input("Choose an id for the vrf :")
                                ospfc=str(int(ospfc)+1)
                                vrfy={"id": idc,
                                    "interface":"GigabitEthernet2/0",
                                    "rd":"3",
                                    "ospf":ospfc}
                                vrfs.append(vrfy)
                                config["routers"][c-1]["vrf"]=vrfs
                                print("Created vrf ....\n",vrfy)
                    
                    if(inter=="FE0/0" or inter == "FastEthernet0/0"):
                        for inte in interfaces:
                            if(inte["name"]=="FastEthernet0/0"):
                                config["routers"][c-1]["interface"][3]["avaible"]="no"
                                system('clear')
                                print("Adding a VRF on interface ", inte["name"], "of the router", where)
                                idc=input("Choose an id for the vrf :")
                                ospfc=str(int(ospfc)+1)
                                vrfy={"id": idc,
                                    "interface":"FastEthernet0/0",
                                    "rd":"3",
                                    "ospf":ospfc}
                                vrfs.append(vrfy)
                                config["routers"][c-1]["vrf"]=vrfs
                                print("Created vrf ....\n",vrfy)

        else:
            flag=0                     
    with open('config.json','w') as f:
        json.dump(config,f,indent=2)
                    
               
                        
        
    return (1)

if __name__ == "__main__":
    
    Adding_client()
