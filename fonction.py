def find_newtwork(inter):
        cont=0
        addr=""
        y = inter["address"].split(".")
        x = inter["mask"].split(".")
        for elt in x:
            cont+=bin(int(elt)).count("1") #find the /32 etc 
        if cont <9:
            addr=str(int(x[0])&int(y[0]))+".0.0.0"
            print(addr)
        elif cont < 17:
            addr=y[0]+"."+str(int(x[1])&int(y[1]))+".0.0"
            print(addr)
        elif cont<25:
            addr=y[0]+"."+y[1]+"."+str(int(x[2])&int(y[2]))+".0"
            print(addr)
        else :
            addr=y[0]+"."+y[1]+"."+y[2]+"."+str(int(x[3])&int(y[3]))
            print(addr)
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
        print(invert)
    elif cont < 17:
        test=255-int(x[1])
        invert="0."+str(test)+".255.255"
        print(invert)
    elif cont<25:
        test=255-int(x[2])
        invert="0.0."+str(test)+".255"
        print(invert)
    else :
        test=255-int(x[3])
        invert="0.0.0."+str(test)
        print(invert)
    return(invert)