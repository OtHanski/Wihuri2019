import i2c as i2c

d=i2c.i2c(13,11)
Vg=1.024

def ADC_settings_write(chan, gain, mod, rate):
    """chan is the channel selected by multiplexer A1=0/A2=1
        gain is for internal amplifier +-FSR 6.144V=0, 4.096V=1,
        2.048=2, 1.024=3,0.512=4,0.256=5
        mod is continuos=0/single shot=1
        samp rate = 128=0, 250=1, 490=2, 920=3, 1600=4, 2400=5, 3300= 6 ja 7
        """
    data1='0'
    data2=''
    Volt=[6.144,4.096,2.048,1.024,0.512,0.256,0.256,0.256]
    #Forming the config bytes according to selections
    """if chan==0:
        data1+="000"
    if chan==1:
        data1+="011" """
    data1+=chan
    data1+=d.databyteconv(gain)[-3:]
    data1+=d.databyteconv(mod)[-1:]
    
    data2+=d.databyteconv(rate)[-3:]
    data2+='00011'
        
    #Write config register
    d.start()
    d.write("10010000") #145
    d.readackbyte()
    d.write("00000001") #writing config reg
    d.readackbyte() 
    d.write(data1) #D15-8
    d.readackbyte()
    d.write(data2) #D7-0
    d.readackbyte()
    #Lisää virheen tarkistus
    d.stop()
    #Voltage range to memory for later user
    Volt=int(d.databyteconv(gain)[-3:], base=2)
    
    return(data1,data2, Volt)

def ADC_select_read_reg(reg):
    """Selects register for reading
        0=ADC data
        1=Conf register"""
    data="000000"
    data+=d.databyteconv(reg)[-2:]
    
    d.start()
    d.write("10010000") #145
    d.readackbyte()
    d.write(data)
    d.readackbyte()
    d.stop()
    
def ADC_read_voltage():
    """Select ADC data register first"""
    d.start()
    d.write("10010001") 
    d.readackbyte()
    b1=d.read(8)
    d.writeackbyte()
    b2=d.read(8)
    d.writeackbyte()
    d.stop()
    num=int(b1+b2[0:4], base=2)
    snum=num if num<=2047 else num-4096
    V=snum/2048*Vg
    return(snum, V)

def ADC_read_register():
    """Select ADC data register first"""
    d.start()
    d.write("10010001") 
    d.readackbyte()
    b1=d.read(8)
    d.writeackbyte()
    b2=d.read(8)
    d.writeackbyte()
    d.stop()
    return(b1, b2)