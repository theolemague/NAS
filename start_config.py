import os
import json
from copy import deepcopy

def parse_json():
    with open('typo.json','r') as f:
        config = json.load(f)

    couples_config=[]
    liste_P=[]
    liste_PE=[]
    for i in config:
        liste_P.append(i)
        for j in config[i]:
            inter = [i,j["router"], j["network"], j["interface"]]
            if (j["router"][:2]=="PE"):
                liste_PE.append(j["router"])
            couples_config.append(inter)
    return (couples_config, liste_P, liste_PE)

def get_dictionnary(liste_tuple, list_P, list_PE):
    liste_complete=[]
    liste_complete.extend(list_PE)
    liste_complete.extend(list_P)
    dico = {}
    network_loopback = 20
    area = 0
    as_nb = 1
    ospf = 100
    min_label=100
    max_label = 199
    liste_dico=[]
    for i in liste_complete:
        dic_inter={
            "name":i,
            "mpls":{
                "mtu":"1500",
                "min_label":str(min_label),
                "max_label":str(max_label)
            },
            "ospf":{
                "id":str(ospf),
                "area":str(area)
            },
            
            "interface":[{
                    "name" : "Loopback0",
                    "address" : "192.168.10."+str(network_loopback),
                    "mask" :"255.255.255.255"
                }
            ]
            
        }

        for j in liste_tuple:
            if j[0] == i: 
                dic_inter["interface"].append({
                        "name" : j[3],
                        "address" : j[2][:-1]+(i[-1]),
                        "mask" : "255.255.255.252",
                        "mpls" : True
                    })
                    

        if i[:2] == "PE":

            for j in liste_tuple:
                if j[1] == i:
                    dic_inter["interface"].append({
                        "name" : "GigabitEthernet1/0",
                        "address" :  j[2][:-1]+str(2),
                        "mask" : "255.255.255.252",
                        "mpls" : True
                    })

            copy_list=deepcopy(list_PE)
            copy_list.remove(i)
            dic_inter["bgp"]={
                "as":str(as_nb),
                "ibgp":copy_list
            }
            dic_inter["interface"].append({
                "name" : "GigabitEthernet2/0",
                "address" : "194.10.2"+i[-1]+".1",
                "mask" : "255.255.255.252",
                "mpls" : False,
            })
            dic_inter["interface"].append({
                "name" : "FastEthernet0/0",
                "address" : "194.20.2"+i[-1]+".1",
                "mask" : "255.255.255.252",
                "mpls" : False
            })
            #dic_inter["ibgp"]=copy_list
        ospf+=100
        min_label+=100
        max_label+=100
        network_loopback+=1
     
        liste_dico.append(dic_inter)

    ports = {}
    for r in liste_dico:
        ports[r["name"]] = ""

    dico["port"]=ports

    dico["routers"]=liste_dico

    return dico

if __name__ == "__main__":
    
    l1,l2,l3 = parse_json()
    my_dico = get_dictionnary(l1,l2,l3)
    
    with open("config.json","w") as f:
        json.dump(my_dico,f,indent=2)
    
    
