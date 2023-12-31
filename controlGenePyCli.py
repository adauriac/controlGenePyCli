#!/usr/bin/env python
import serial
import minimalmodbus
import serial.tools.list_ports as port_list
import time,sys
"""
                                 WITH A POLLING WATCHDOG (NO THREAD OR RACE)
class geneControler : can connect and read/write registers
at initialization one can provide,or not, a function to treat the error,
if no function is provided an exit is performed
at connect a function can be provided to choose the serial port,
if no function provided take the first encountered.


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

class geneControler:
    ou = []
    quoi = []
    index= dict()
    vals = []
    types = [] # "led", "button", "output", "input"
    instrument = "";
    def __init__(self,myFun=""):
        self.errorTreat = myFun;
        self.quoi.append("Arret d'urgence");
        self.ou.append(0x65);
        self.index["Arret d'urgence"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("led")

        self.quoi.append("Defaut critique");
        self.ou.append(0x66);
        self.index["Defaut critique"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("led")

        self.quoi.append("Mesure debit");
        self.ou.append(0x68);
        self.index["Mesure debit"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("self.output")

        self.quoi.append("Mesure puissance");
        self.ou.append(0x6B);
        self.index["Mesure puissance"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("output")

        self.quoi.append("Etat du procede");
        self.ou.append(0x6E);
        self.index["Etat du procede"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("led")

        self.quoi.append("Tension PFC ");
        self.ou.append(0x72);
        self.index["Tension PFC "] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("output")

        self.quoi.append("Courant pont");
        self.ou.append(0x7F);
        self.index["Courant pont"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("output")

        self.quoi.append("Puissance limite basse");
        self.ou.append(0x96);
        self.index["Puissance limite basse"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("input")

        self.quoi.append("Puissance limite haute");
        self.ou.append(0x97);
        self.index["Puissance limite haute"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("input")

        self.quoi.append("Debit bas");
        self.ou.append(0xA0);
        self.index["Debit bas"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("input")

        self.quoi.append("Debit haut");
        self.ou.append(0xA1);
        self.index["Debit haut"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("input")

        self.quoi.append("Consigne puissance");
        self.ou.append(0xB2);
        self.index["Consigne puissance"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("input")

        self.quoi.append("Consigne debit");
        self.ou.append(0xB3);
        self.index["Consigne debit"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("input")

        self.quoi.append("Generateur");
        self.ou.append(0xBB);
        self.index["Generateur"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("button")

        self.quoi.append("Gaz");
        self.ou.append(0xBC);
        self.index["Gaz"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("button")

        self.quoi.append("Plasma");
        self.ou.append(0xBD);
        self.index["Plasma"] = len(self.ou)-1;
        self.vals.append(-1)
        self.types.append("button")
        # FIN __init__()
        
    def readRegister(self,add):
        """
        return the int value read, exit if can't read
        """
        # print(f"entering readRegister {add}");
        readingPossible = False    
        ok = 1
        ans = [-1]
        try:
            ans = self.instrument.read_registers(add,1)
        except :
            sys.stdout.writelines("readRegister: Could not read register at 0x%x = %d\n"%(add,add))
            if add == ALIVE_ADDRESS: # ie probably a test isAlive()
                sys.stdout.writelines("The board is probably not powered\n")
            sys.stdout.flush()
            ok = 0
        if not ok:
            if self.treatErr!= "":
                self.errorTreat(2)
            else:
                exit(2) #read error
        # print(f"leaving readRegister {add}")
        return ans[0]
    # FIN  def readRegister(self,add):

    def getRegisters(self):
        """
        set vals and return a string ready to be printed
        if a reading fails an empty string is return instead
        """
        ans = ""
        ok = 1
        for i in range(len(self.ou)):
            v = self.readRegister(self.ou[i])
            self.vals[i] = v
            ans += "%2d Ox%x %3d %26s %5d  %s\n"%(i,self.ou[i],self.ou[i],self.quoi[i],self.vals[i],self.types[i])
        return ans
    # FIN def getRegisters(self):

    def isAlive(self):
        ans = self.readRegister(ALIVE_ADDRESS)
        return ans==ALIVE_VALUE
    # FIN def isAlive():

    def writeRegister(self,add,value):
        """
        call errorTreat or exit if can't write
        """
        # print(f"entering writeRegister {add}")
        readingPossible = False
        ok = 1
        try:
            self.instrument.write_register(add,value)
        except :
            sys.stdout.writelines("writeRegister: Could not write register at 0x%x = %d\n"%(add,add))
            sys.stdout.flush()
            ok = 0
        if not ok:
            if self.treatErr!= "":
                self.errorTreat(1)
            else:
                exit(1) # write error
        #print(f"leaving writeRegister {add}")
    # FIN def writeRegister(add,value):

    def readRegister(self,add):
        """
        return the int value read, exit if can't read
        """
        # print(f"entering readRegister {add}");
        readingPossible = False    
        ok = 1
        ans = [-1]
        try:
            ans = self.instrument.read_registers(add,1)
        except :
            ok = 0
        if not ok:
            if self.errorTreat!= "":
                self.errorTreat(2)
            else:
                exit(2) #read error
        # print(f"leaving readRegister {add}")
        return ans[0]
    # FIN  def readRegister(add)
    
    def connect(self):
        """
        connect the instrument
        return True if ok
               a string describing the error else
        """
        ports = list(port_list.comports())
        # choice of the port to use
        if len(ports)==0:
            return "No serial port available"
        lesInstruments = [] # instruments that can be used
        for k,port in enumerate(ports): # try to use all listed ports
            ser = serial.Serial(port.device)
            ser.timeout = TIMEOUT # seconds
            instrument = minimalmodbus.Instrument(ser, SLAVE)
            instrument.serial.baudrate = BAUD
            instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
            instrument.mode = 'rtu'
            # instrument.debug = True
            instrument.timeout = ser.timeout
            try:
                ans = instrument.read_registers(ALIVE_ADDRESS,1)
                lesInstruments.append(instrument)        
            except :
                pass
            ser.close()
        if len(lesInstruments)==0:
            return "no serial port connected to the generator"
        if len(lesInstruments)>1 :
            return "%d port connected to a generator, please plug only the desired one"%(len(lesInstruments))
        # use the port with index 0
        port = ports[0]
        ser = serial.Serial(port.device)
        ser.timeout = TIMEOUT # seconds
        self.instrument = minimalmodbus.Instrument(ser, SLAVE)
        self.instrument.serial.baudrate = BAUD
        self.instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
        self.instrument.mode = 'rtu'
        self.instrument.timeout = ser.timeout
        # self.instrument.debug = True
        sys.stdout.writelines("using %s at %d baud parity %c\n"%(self.instrument.serial.name,self.instrument.serial.baudrate,self.instrument.serial.parity))
        sys.stdout.flush()
        return True
    # FIN connect(self)
    
# FIN class geneControler
# ***********************************************************************************

if __name__ == '__main__':
    import msvcrt

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
    # FIN class nonBlockingString:
    # ***********************************************************************************
    
    def myFun(p):
        """
        function called in case of error, with the parameter p:
        p=1 write error timeouut
        p=2 read error timeout
        p=3 no serial port
        p=4 not alive (ie bad reading by the watchDog)
        """
        print(f"oops j'ai recu la valeur {p}")
        exit(p)
    # FIN myFun(p)
    # ***********************************************************************************

    myGene = geneControler(myFun)
    ans = myGene.connect()
    if ans != True:
        print(ans)
        exit(1)
    mySt = nonBlockingString() # pour faire une lecture non bloquante du clavier
    somethingNew = True
    lastCheckAlive = 0
    cpt = 0
    while True:
        time.sleep(0.1)
        cpt += 1
        currentTime = time.time()
        if currentTime - lastCheckAlive > WATCHDOGTIMESEC:
            lastCheckAlive = currentTime
            if not myGene.isAlive():
                sys.stdout.writelines("The connection is down !")
                sys.stdout.flush()
                break
        if somethingNew:
            somethingNew = False
            ans = myGene.getRegisters()
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
        sys.stdout.writelines("\n")
        sys.stdout.flush()
        if o<0 or o>=len(myGene.ou):
            sys.stdout.writelines("%d is not the index of a register\n"%o)
            sys.stdout.flush()
            continue
        if q<0 or q>=65536:
            sys.stdout.writelines("the value %d is out of bonds\n"%q)
            sys.stdout.flush()
            continue
        myGene.vals[o] = q
        myGene.writeRegister(myGene.ou[o],q)
