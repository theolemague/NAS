import os
import json

def Adding_client():
    with open('config_test.json','r+') as f:
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
            print(liste_PE)
            where=input("\n On which PE do you want to add a client ? :")
            for r in routers :
                if(r["name"]==where):
                    interfaces=r["interface"]
                    for int in interfaces:
                        if(int["name"]!="Loopback0" and int["name"]!="GigabitEthernet1/0"):
                            print(int)
        else:
            flag =0
    return (1)

if __name__ == "__main__":
    
    Adding_client()
