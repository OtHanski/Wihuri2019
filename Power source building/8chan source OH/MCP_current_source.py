import i2c as i2c

d=i2c.i2c(13,11)
Vg=1.024
PGA=1 #Amplifier setting

def MCP_read():
    
    #Read from current monitor adc MCP3425
    res=d.read_device('1101000', 3)
    return(res)

def MCP_settings_write(mod, rate, gain):
    """mod: 1=cont conv, 0=single
        rate: 0=12 bit 240 sps, 1=14 bit 60 sps, 2=16bit 15sps
        gain: 0=1 (V/Vin), 1=2, 2=4, 3=8"""
    data='000'
    data+=d.databyteconv(mod)[-1:]
    data+=d.databyteconv(rate)[-2:]
    data+=d.databyteconv(gain)[-2:]
    
    d.start()
    d.write(208) #Write
    d.readackbyte()
    d.write(data)
    d.readackbyte()
    d.stop()
    return(data)


def MCP_read_voltage():
    
    #Read voltage from adc MCP3425 assuming 1V/vin and 16bit
    res=d.read_device('1101000', 3)
    num=int(res[0]+res[1], base=2)
    
    snum=num if num<=2**15 else num-2**16 
    V=snum*2.048/(2**16)*PGA
    return(snum, V)
    
    
    