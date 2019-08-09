import RPi.GPIO as GPIO
import re
import relays
""" 

11.06.2019 Updated version, removing old relay control and adding new. Renamed to digipot_2 /JA
 """

# Address is string of three bits e.g. "000"

class digipot:
    """Class for controlling DS1803 digital potentiometer with RPI"""

    def __init__(self, address, SDA=3, SCL=5):
        # Pin numbers for data self.SDA and clock SDC and digipot addresses as binary string list
        # Same order: [000;0 ,  000;1  , 100;0  ,  100;1]
		# jj_new = [["000", 0, 0], ["000", 1, 1], ["001", 0, 2], ["001", 1, 3], ["010", 0, 4], ["010", 1, 5], ["011", 0, 6], ["011", 1, 7]]
		
        GPIO.setmode(GPIO.BOARD)  # Pins addressed according to physical pins

        for i in address:
            if re.search('[a-zA-Z2-9]', i[0]) and not (len(i[0]) == 3):
                raise ValueError('Address string is not in correct form')
        # Serial com pins to outputs
        GPIO.setup(SCL, GPIO.OUT)
        GPIO.setup(SDA, GPIO.OUT)
        # Setting pins to low state
        GPIO.output(SCL, 0)
        GPIO.output(SDA, 0)

        self.address = address
        self.SDA = SDA
        self.SCL = SCL
        
        # Relay control
        self.relays = relays.relays()
        
        # Relay control pins as outputs
        # for n in self.address:
        #    GPIO.setup(n[2], GPIO.OUT)
        #    GPIO.output(n[2], 1)
        # Change the chip address
        # def changeaddr(self, address): #address is string of three bits e.g. "000"
        # if not(re.search('[a-zA-Z2-9]',address)) and len(address)==3:
        #   self.control="0101"+address
        # else:
        #  raise ValueError('Address string is not in correct form')

    def write(self, pot, value):  # Pot number is the index in address list
        if (value >= 0):  # If current isn't negative, switch off the relay
            self.channelground(pot, 0)

        data = self.databyteconv(value)
        ctrlbyte = "0101" + self.address[pot][0] + "0"  # control for writing
        if self.address[pot][1] == 0:
            combyte = "10101001"
        else:
            combyte = "10101010"  # if not pot 0, pot 1 is assumed #Check

        # start condition
        GPIO.output(self.SDA, 1)
        GPIO.output(self.SCL, 1)
        GPIO.output(self.SDA, 0)
        GPIO.output(self.SCL, 0)

        # write ctrlbyte
        for n in ctrlbyte:
            GPIO.output(self.SDA, int(n))
            GPIO.output(self.SCL, 1)
            GPIO.output(self.SCL, 0)
        # acknowledgement
        self.readackbyte()

        # write commandbyte
        for n in combyte:
            GPIO.output(self.SDA, int(n))
            GPIO.output(self.SCL, 1)
            GPIO.output(self.SCL, 0)
        # acknowledgement
        self.readackbyte()

        # write data byte
        for n in data:
            GPIO.output(self.SDA, int(n))
            GPIO.output(self.SCL, 1)
            GPIO.output(self.SCL, 0)
        # acknowledgement
        self.readackbyte()
        self.stop()
        if (value == -1):  # If current is negative, current to zero and switch on the relay
            self.channelground(pot, 1)

            # Check relay status: on/off

#    def checkStatus(self, number):
#      status = GPIO.input(self.relays[number - 1])
#        return 1

    # Reading the state of a pot
    def read(self, pot):
        ctrlbyte = "0101" + self.address[pot][0] + "1"  # control for reading
        # start condition Start SCL - high SDA - down
        GPIO.output(self.SDA, 1)
        GPIO.output(self.SCL, 1)
        GPIO.output(self.SDA, 0)
        GPIO.output(self.SCL, 0)
        # write ctrlbyte
        for n in ctrlbyte:
            GPIO.output(self.SDA, int(n))
            GPIO.output(self.SCL, 1)
            GPIO.output(self.SCL, 0)

        self.readackbyte()

        # SDA pin to read
        GPIO.setup(self.SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # read pot 0
        pot0 = ""
        for n in range(0, 8):
            GPIO.output(self.SCL, 1)
            pot0 += str(GPIO.input(self.SDA))
            GPIO.output(self.SCL, 0)
        # Write ack byte
        self.writeackbyte()

        # SDA pin to read
        GPIO.setup(self.SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        pot1 = ""
        # read pot 1
        for n in range(0, 8):
            GPIO.output(self.SCL, 1)
            pot1 += str(GPIO.input(self.SDA))
            GPIO.output(self.SCL, 0)
        # Write ack byte
        self.writeackbyte()
        self.stop()
        if self.address[pot][1] == 0:
            return pot0
        if self.address[pot][1] == 1:
            return pot1
        else:
            return pot0, pot1

    # END reading--------------------------------------------

    # create stop condition
    def stop(self):
        GPIO.output(self.SDA, 0)
        GPIO.output(self.SCL, 1)
        GPIO.output(self.SDA, 1)
        GPIO.output(self.SCL, 0)

    def close(self):
        GPIO.cleanup()

    def databyteconv(self, value):
        if type(value) is int:
            if value<0:
                apu=0
            else:
                apu=value

            data = str(bin(apu)).split('b', 1)[1]
            if len(data) > 8: data = "00000000"  # Error in data puts pot to 0
            data = "00000000"[0:8 - len(data)] + data
        elif type(value) is str:
            data = value
            if len(data) > 8: data = "00000000"  # Error in data puts pot to 0
            data = "00000000"[0:8 - len(data)] + data
        else:
            raise Exception("type(value) = {}".format(repr(value)))
        return data

    def readackbyte(self):
        GPIO.setup(self.SDA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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

    # Control of grounding relays
    def channelground(self, number, value):
        self.relays.set_relay(self.address[number][2], value)
        #GPIO.output(self.address[number][2], value)
