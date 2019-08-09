# -*- coding: utf-8 -*-
"""
11.6.2019 First version of relay control class /JA
"""


import RPi.GPIO as GPIO

class relays:
    """Class for bookkeeping and controlling relay states"""
    
    def __init__(self, SRCLK=18, RCLK=15, SER=12, n = 8):
        """
		Creates a object of relays and initiates all to grounded (1) state.
		
		n is the number of relays
		"""
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(SRCLK, GPIO.OUT)
        GPIO.setup(RCLK, GPIO.OUT)
        GPIO.setup(SER, GPIO.OUT)
        GPIO.output( SRCLK,0)
        GPIO.output( RCLK,0)
        
        self.SRCLK = SRCLK
        self.RCLK = RCLK
        self.SER = SER
        
        if n < 1 or n > 16:
            n=8
        self.relay_state = [1]*n  #Creating array representing relay states
        self.num = 0
        self.update_num()         #Updating number representing present relay states
        self.update_relays()      #Update relays to the state set before
        
    def update_num(self):
        """ Updates the number representing relay state based on the relay array"""
        i = 0
        num = 0
        for b in self.relay_state:
            if b == 1:
                num += 2**i
            i += 1
        self.num = num
    
    def get_binary(self):
        return '{0:08b}'.format(self.num)
        
    def set_relay(self, i, state):
        """ Sets relay at index i to the state stat (0 or 1)"""
        if i >= 0 and i < len(self.relay_state):
                if state > 0:
                        state = 1
                else:
                        state = 0
        self.relay_state[i] = state
        self.update_num()
        self.update_relays()
        
    def update_relays(self):
        """ Updates the relays to the state represented by relay_state and num """
        byt='{0:08b}'.format(self.num)
        for n in range(0,8):
            GPIO.output(self.SER, int(byt[n]) )
            # print(byt[n])
            GPIO.output(self.SRCLK, 1 )
            GPIO.output(self.SRCLK, 0 )
        GPIO.output(self.RCLK, 1 )
        GPIO.output(self.RCLK, 0 )
        

if __name__ == "__main__":
    r = relays()
    print(r.get_binary())
    
    for i in range(0,8):
        r.set_relay(i, 0)
        print(r.get_binary())

        
    
