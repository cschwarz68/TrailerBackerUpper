import pigpio as io


    

class IO(io.pi):
    def set_low(self,pin):
        super().write(pin,0)
    
    def set_high(self,pin):
        super().write(pin,1)

    def set_output(self,pin):
        super().set_mode(pin,io.OUTPUT)
    
    def set_input(self,pin):
        super().set_mode(pin,io.INPUT)

   