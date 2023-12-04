#!/usr/bin/env python
import serial
import minimalmodbus
import serial.tools.list_ports as port_list

"""
                                 VERSION SANS TEST PERMANENT
Connecte a BAUD,'N',8,1. La com choisie est demandée au clavier s'il y a plus d'une seule possibilité.
En cas de non-connexion un message est affiché et le programme se termine
En cas de lecture ou d'écriture non finie apres TIMEOUT seconde message est affiché et le programme se termine
"""
TIMEOUT = 2 # secondes
BAUD = 9600
SLAVE = 3
ALIVE_ADDRESS = 205
ALIVE_VALUE = 330

def getRegisters():
    """
    set vals and return a string ready to be printed
    if a reading fails an empty string is return instead
    """
    ans = ""
    ok = 1
    for i in range(len(ou)):
        v = readRegister(ou[i])
        vals[i] = v
        ans += "%2d Ox%x %3d %26s %5d  %c\n"%(i,ou[i],ou[i],quoi[i],vals[i],'*' if writes[i] else  ' ')
    return ans
# FIN def getRegisters():

def isAlive():
    v = readRegister(ALIVE_ADDRESS)
    return v==ALIVE_VALUE
# FIN def isAlive():

def writeRegister(add,value):
    """
    exit if can't write
    """
    ok = 1
    try:
        instrument.write_register(add,value)
    except :
        print("Could not write register at 0x%x = %d"%(add,add))
        ok = 0
    if not ok:
        exit(1) # write error
# FIN def writeRegister(add,value):

def readRegister(add):
    """
    return the int value read, exit if can't read
    """
    ok = 1
    ans = [-1]
    try:
        ans = instrument.read_registers(add,1)
    except :
        print("Could not read register at 0x%x = %d"%(add,add))
        if add  == ALIVE_ADDRESS:
            print("The board is probably not powered")
        ok = 0
    if not ok:
        exit(2) #read error
    return ans[0]
# FIN  def readRegister(add):
  
quoi = []
ou = []
index= dict()
vals = []
writes = []

quoi.append("Generateur");
ou.append(0xBB);
index["Generateur"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Gaz");
ou.append(0xBC);
index["Gaz"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Plasma");
ou.append(0xBD);
index["Plasma"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Arret d'urgence");
ou.append(0x65);
index["Arret d'urgence"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Defaut critique");
ou.append(0x66);
index["Defaut critique"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Etat du procede");
ou.append(0x6E);
index["Etat du procede"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Consigne puissance");
ou.append(0xB2);
index["Consigne puissance"] = len(ou)-1;
vals.append(-1)
writes.append(True)

quoi.append("Consigne debit");
ou.append(0xB3);
index["Consigne debit"] = len(ou)-1;
vals.append(-1)
writes.append(True)

quoi.append("Mesure puissance");
ou.append(0x6B);
index["Mesure puissance"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Mesure debit");
ou.append(0x68);
index["Mesure debit"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Courant pont");
ou.append(0x7F);
index["Courant pont"] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Tension PFC ");
ou.append(0x72);
index["Tension PFC "] = len(ou)-1;
vals.append(-1)
writes.append(False)

quoi.append("Puissance limite basse");
ou.append(0x96);
index["Puissance limite basse"] = len(ou)-1;
vals.append(-1)
writes.append(True)

quoi.append("Puissance limite haute");
ou.append(0x97);
index["Puissance limite haute"] = len(ou)-1;
vals.append(-1)
writes.append(True)

quoi.append("Debit bas");
ou.append(0xA0);
index["Debit bas"] = len(ou)-1;
vals.append(-1)
writes.append(True)

quoi.append("Debit haut");
ou.append(0xA1);
index["Debit haut"] = len(ou)-1;
vals.append(-1)
writes.append(True)

writables = []
for k,f in enumerate(writes):
    if f:
        writables.append(k)
addWritables = list(map(lambda x:ou[x],writables))

# ######################################################################################
#                               CONNECTION
# ######################################################################################
ports = list(port_list.comports())
# choice of the port to use
if len(ports)==0:
    print("No serial port available")
    exit(3) # no serial port
elif len(ports)>1:
    print("there are several possible ports")
    for k,p in enumerate(ports):
        ser = serial.Serial(p.device)
        print("%d %s"%(k,ser.name))
        ser.close()
    while True:
        ans = input("choose one in [0,%d] "%(len(ports)-1))
        try:
            k = int(ans)
            if k>=0 and k<len(ports):
                break
        except:
            pass
else:
    k = 0
    
port = ports[k].device
ser = serial.Serial(port)
ser.timeout = TIMEOUT # seconds
instrument = minimalmodbus.Instrument(ser, SLAVE)
instrument.serial.baudrate = BAUD
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.mode = 'rtu'
# instrument.debug = True
instrument.timeout = ser.timeout
print("using %s at %d baud parity %c"%(ser.name,instrument.serial.baudrate,instrument.serial.parity))
isAlive()

# ######################################################################################
#                               INFINITE LOOP
# ######################################################################################
while True:
    ans = getRegisters()
    if ans=="":
        exit(1)
    else:
        print(ans)
    ans = input("entrer le numéro du registre et la valeur a y mettre, ou q pour quitter ")
    if ans=='q':
        break
    ans = ans.split()
    if len(ans)!=2:
        continue
    try:
        ans = list(map(int,ans))
    except:
        continue
    o,q = ans
    if o<0 or o>=len(ou):
        print("the register %d is not a writable register"%o)
        continue
    if not ou[o] in addWritables:
        print("This register is not writeable")
        continue
    if q<0 or q>=65536:
        print("the value %d is out of bonds"%q)
        continue
    vals[o] = q
    # instrument.write_registers(ou[o],[vals[o]])
    writeRegister(ou[o],q)
exit(0)
