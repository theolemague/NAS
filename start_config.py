import os
import json
from copy import deepcopy

def get_values():
    nb_routers=int(input("How many routers do you want ? :"))
    nb_pe=int(input("How many PE ? :"))
    nb_p=nb_routers-nb_pe
    #list_router=["R"+str(i) for i in range(1, int(nb_routers)+1)]
    list_PE=["PE"+str(i) for i in range(1, int(nb_pe)+1)]
    list_P=["P"+str(i) for i in range(1, nb_p + 1)]
    network = "172.26"
    while True :
        res=input("Enter sur network /16 of the backbone (default 172.26, enter to skip) : ")
        if res == "": break
        elif len(res.split(".")) == 2 :
            network = res
            break
        else : print(res,"is a wrong network")
    print("Network choose :", network+".0.0/16")
    network += "."
    list_tuple=[]

    network_count=20
    print("Backbone typology is :")
    for i in range(1, len(list_P)):
        inter=["P"+str(i),"P"+str(i+1), network+str(network_count)+".0"]
        list_tuple.append(inter)
        print(inter)
        network_count+=1
    inter=[list_PE[-1],list_P[-1],network+str(network_count)+".0"]
    list_tuple.append(inter)
    print(inter)
    network_count+=1
    for i in range(len(list_PE)-1):
        inter=[list_PE[i],list_P[i],network+str(network_count)+".0"]
        print(inter)
        list_tuple.append(inter)
        network_count +=1

    response=input("Is the typology right ? y/n : ")
    if response:
       if (response[0] == "n"):
            while (True):
                print("Please enter the router couple and the network separate with ',' :")
                print("ex :  r1,r2,192.168.10.0")
                print("all networks are /30")
                print("type done when you're finished ")
                reponse =input("Response : ")
                if reponse == "done":
                    break
                else :
                    reponse.split(",")
                    list_tuple.append(reponse)
    return (list_tuple, list_P, list_PE)

def parse_json():
    with open('typo.json','r') as f:
        config = json.load(f)

    couples_config=[]
    liste_P=[]
    liste_PE=[]
    for i in config:
        liste_P.append(i)
        #print(config[i])
        for j in config[i]:
            inter = [i,j["router"], j["network"], j["interface"]]
            if (j["router"][:2]=="PE"):
                liste_PE.append(j["router"])
            #print(i[j])
            couples_config.append(inter)
    print(liste_PE)
    print(liste_P)
    print(couples_config)
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
            "port": "",
            "name":i,
            "mpls":{
                "mtu":"1560",
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
                        "address" :  j[2][:-1]+str(int(i[-1])+1),
                        "mask" : "255.255.255.252",
                        "mpls" : True
                    })

            #print(list_PE)
            copy_list=deepcopy(list_PE)
            #print(copy_list)
            copy_list.remove(i)
            #print(copy_list)
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
    
    
