from grove.adc import ADC
import math

Beta=4275
R0=100000

adc=ADC()

def temp_c():
    
    value=adc.read(0)
    
    if value<=0:
        raise ValueError("Temperature sensor return ADC=0")
    R=R0*(1023.0/value-1.0)

    temp=1.0/(math.log(R/R0)/Beta+1/298.15)-273.15

    return temp

def temp_k():   

    return temp_c() +273.15


if __name__ == "__main__":
    print("C: ",temp_c())
    print("K: ",temp_k())
