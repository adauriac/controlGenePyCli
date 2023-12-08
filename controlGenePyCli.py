#!/usr/bin/env python
import serial
import minimalmodbus
import serial.tools.list_ports as port_list
import time,sys
import msvcrt
"""
                                 WITH A POLLING WATCHDOG (NO THREAD OR RACE)
Connection at BAUD,'N',8,1.
The choosen COM is asked to keyboard if there are more than one.
An infinite loop tests the keyboard in a NON blocking way therefore the loop is short.
At each beginning of the loop the current time is compared to the time of the last test of the connection.
If the last test is too old a new test is performed.
If a reading/writing of a register is too long, the program aborts.
"""

TIMEOUT = 0.1 # for reading/writing register a real number in secondes 
BAUD = 9600
SLAVE = 3
ALIVE_ADDRESS = 205
ALIVE_VALUE = 330
WATCHDOGTIMESEC = 1  # a float in second, a new test is made is 

class nonBlockingString:
    """
    Cette classe permet une lecture NON bloquente du clavier.
    La chaine se termine par '\\n' ou '\\r', elle n'est retournee
    par getKbd() que lorsqu'elle est complete, sinon None est retourne
    """
    def __init__(self):
        self.str = ""
    def getKbd(self):
        """
        retourne la chaine si elle est complete (finie par \\n ou \\r) None sinon
        """
        if msvcrt.kbhit():
            self.car = msvcrt.getche()
            self.str += self.car.decode()
            if self.car == b'\r' or self.car == b'\n':
                aux = self.str
                self.str = ""
                return aux

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
    ans = readRegister(ALIVE_ADDRESS)
    return ans==ALIVE_VALUE
# FIN def isAlive():

def writeRegister(add,value):
    """
    exit if can't write
    """
    # print(f"entering writeRegister {add}")
    readingPossible = False
    ok = 1
    try:
        instrument.write_register(add,value)
    except :
        sys.stdout.writelines("writeRegister: Could not write register at 0x%x = %d\n"%(add,add))
        sys.stdout.flush()
        ok = 0
    if not ok:
        exit(1) # write error
    #print(f"leaving writeRegister {add}")
# FIN def writeRegister(add,value):

def readRegister(add):
    """
    return the int value read, exit if can't read
    """
    # print(f"entering readRegister {add}");
    readingPossible = False    
    ok = 1
    ans = [-1]
    try:
        ans = instrument.read_registers(add,1)
    except :
        sys.stdout.writelines("readRegister: Could not read register at 0x%x = %d\n"%(add,add))
        if add == ALIVE_ADDRESS: # ie probably a test isAlive()
            sys.stdout.writelines("The board is probably not powered\n")
        sys.stdout.flush()
        ok = 0
    if not ok:
        exit(2) #read error
    # print(f"leaving readRegister {add}")
    return ans[0]
# FIN  def readRegister(add):

cpt = 0
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
    sys.stdout.writelines("No serial port available\n")
    sys.stdout.flush()
    exit(3) # no serial port
elif len(ports)>1:
    sys.stdout.writelines("there are several possible ports\n")
    sys.stdout.flush()
    for k,p in enumerate(ports):
        ser = serial.Serial(p.device)
        sys.stdout.writelines("%d %s\n"%(k,ser.name))
        sys.stdout.flush()
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
sys.stdout.writelines("using %s at %d baud parity %c\n"%(ser.name,instrument.serial.baudrate,instrument.serial.parity))
sys.stdout.flush()
isAlive()

cpt = 0
#######################################################################################
#                               INFINITE LOOP
#######################################################################################
mySt = nonBlockingString() # pour faire une lecture non bloquante du clavier
somethingNew = True
lastCheckAlive = 0
while True:
    time.sleep(0.1)
    cpt += 1
    currentTime = time.time()
    if currentTime - lastCheckAlive > WATCHDOGTIMESEC:
        lastCheckAlive = currentTime
        if not isAlive():
            sys.stdout.writelines("The connection is down !")
            sys.stdout.flush()
            break
    if somethingNew:
        somethingNew = False
        ans = getRegisters()
        sys.stdout.writelines(ans)
        sys.stdout.writelines("\nenter the register number and the value to set, or q for quit : ")
        sys.stdout.flush()
    # ans = input("entrer le numéro du registre et la valeur a y mettre, ou q pour quitter ")
    ans = mySt.getKbd()
    if ans==None:
        continue
    somethingNew = True
    sys.stdout.writelines("\n")
    sys.stdout.flush()
    if ans=='q\r':
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
        sys.stdout.writelines("the register %d is not a writable register\n"%o)
        sys.stdout.flush()
        continue
    if not ou[o] in addWritables:
        sys.stdout.writelines("This register is not writeable\n")
        sys.stdout.flush()
        continue
    if q<0 or q>=65536:
        sys.stdout.writelines("the value %d is out of bonds\n"%q)
        sys.stdout.flush()
        continue
    vals[o] = q
    writeRegister(ou[o],q)
