import json
import telnetlib

preload_str= "!\n\n!\nversion 12.4\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nno service password-encryption\n!\n"
end_str = "control-plane\n!\n!\n!\n!\nline con 0\n exec-timeout 0 0\n logging synchronous\nline aux 0\nline vty 0 4\n login!\n!\nend\n"


def config_router(port, router):

    tn = telnetlib.Telnet("localhost", port)
    tn.write(b'en\r\n')
    tn.write(b'conf t\r\n')
    for inter in router["interfaces"]:
        print(inter)
        tn.write(bytes("interface "+inter["name"]+"\r\n",'utf-8'))
        tn.write(bytes("ip address "+inter["address"]+" "+inter["mask"]+"\r\n", "utf-8"))
        tn.write(b"no shutdown\r\n")
        tn.write(b"exit\r\n")
    tn.write(b'do write\r\n')
    print(tn.read_very_eager().decode("ascii"))


if __name__ == "__main__":

    config = 0
    with open('config.json','r') as f:
        config = json.load(f)
    routers = config["routers"]
    for router in routers :
        config_router(router["port"], router)
        