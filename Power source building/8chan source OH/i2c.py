import RPi.GPIO as GPIO
import re


class i2c:
    """Class for I2C communication with RPI"""

    def __init__(self, SDA, SCL):
        # Pin numbers for data self SDA and clock SDC

        GPIO.setmode(GPIO.BOARD)  # Pins addressed according to physical pins

        # Serial com pins to outputs
        GPIO.setup(SCL, GPIO.OUT)
        GPIO.setup(SDA, GPIO.OUT)
        # Setting pins to low state
        GPIO.output(SCL, 0)
        GPIO.output(SDA, 0)

        self.SDA = SDA
        self.SCL = SCL
        
    def write(self, value):
        """Raw write of byte number or binary string to I2C.
            No automatic start or stop conditions."""
        if type(value) is int: data = self.databyteconv(value)
        
        elif type(value) is str:
            test=set(value)
            if test == {'0', '1'} or test == {'0'} or test == {'1'}:
                data = value
            else:
                raise ValueError("That is not a binary string!")
    
            if len(data) > 8: data = data[0:8]
            
        else:
            raise Exception("type(value) = {}".format(repr(value)))

        # write value
        for n in data:
            GPIO.output(self.SDA, int(n))
            GPIO.output(self.SCL, 1)
            GPIO.output(self.SCL, 0)
        return data

   
    def read(self, length):
        """Read length bits from I2C.
            No automatic start or stop conditions."""
        # SDA pin to read
        if self.SDA == 3: GPIO.setup(self.SDA, GPIO.IN) #Other channels needs pull up
        else: GPIO.setup(self.SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        data = ""
        for n in range(0, length):
            data += str(GPIO.input(self.SDA)) #First bit is already waiting
            GPIO.output(self.SCL, 1)
            GPIO.output(self.SCL, 0)
            
        # SDA pin to write
        GPIO.setup(self.SDA, GPIO.OUT)
        return data

    # END reading--------------------------------------------

    # create stop condition
    def stop(self):
        GPIO.output(self.SDA, 0)
        GPIO.output(self.SCL, 1)
        GPIO.output(self.SDA, 1)
        GPIO.output(self.SCL, 0)
    def start(self):
        # start condition Start SCL - high SDA - down
        GPIO.output(self.SDA, 1)
        GPIO.output(self.SCL, 1)
        GPIO.output(self.SDA, 0)
        GPIO.output(self.SCL, 0)

    def close(self):
        GPIO.cleanup()

    def databyteconv(self, value):
        if type(value) is int:
            data = str(bin(value)).split('b', 1)[1]
            if len(data) > 8: data = "00000000"  # Error in data gives 0
            data = "00000000"[0:8 - len(data)] + data
        elif type(value) is str:
            try:
                int(value, base=2)
            except:
                raise ValueError("That is not a binary string!")
                pass
                
            data = value
            if len(data) > 8: data = "00000000"  # Error in data gives 0
            data = "00000000"[0:8 - len(data)] + data            
        else:
            raise Exception("type(value) = {}".format(repr(value)))
        return data

    def readackbyte(self):
        if self.SDA == 3: GPIO.setup(self.SDA, GPIO.IN) #Other channel needs pull up
        else: GPIO.setup(self.SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.output(self.SCL, 1)
        ack = GPIO.input(self.SDA)
        GPIO.output(self.SCL, 0)
        GPIO.setup(self.SDA, GPIO.OUT)
        GPIO.output(self.SDA, 0)
        # print(ack)
        return ack

    def writeackbyte(self):
        GPIO.setup(self.SDA, GPIO.OUT)
        # write acknowledgement
        GPIO.output(self.SDA, 0)
        GPIO.output(self.SCL, 1)
        GPIO.output(self.SCL, 0)

    def read_device(self, address, n):
        """Higher level method to read n bytes from address.
            Address is cutted or given in 7 bit form without W/R bit.
            Read bit =! is added to address.
            Address format is either binary string or int.
            ackbyte error returns -1"""
        self.start()
        if type(address) is str and len(address)==7:
            self.write(self.databyteconv(address)[1:8]+'1')
        elif type(address) is str and len(address)==8:
            self.write(self.databyteconv(address)[0:7]+'1')
        if self.readackbyte()==1:
            return -1
        res=[]
        for n in range(0,n):
            res.append(self.read(8))
            self.writeackbyte()
        self.stop()
        return(res)
    

