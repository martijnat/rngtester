#!/usr/bin/env python2
import sys
import math

black                   = "\x1b[30m"
red                     = "\x1b[31m"
green                   = "\x1b[32m"
yellow                  = "\x1b[33m"
blue                    = "\x1b[34m"
magenta                 = "\x1b[35m"
cyan                    = "\x1b[36m"
white                   = "\x1b[37m"
color_normal            = "\x1b[0m"
color_bold              = "\x1b[1m"

def print_status(description,simple_test=False,hard_test=False):
    if hard_test:
        print_nice(description,green," OK ")
    elif simple_test:
        print_nice(description,yellow,"Weak")
    else:
        print_nice(description,red+color_bold,"Fail")

def print_nice(description,color,status):
    desc = description + " " + "-"*(60-len(description))
    sys.stdout.write("%60s [%s%04s%s]\n"%(desc,color,status,color_normal))


class RngTest():
    def __init__(self):
        self.charbuffer     = []
        self.BufferByteSize = 1

    def process_byte(self,char):
        self.charbuffer.append(ord(char))
        if len(self.charbuffer)>=self.BufferByteSize:
            self.update_buffer(self.charbuffer)
            self.update_int(self.buffer_to_int(self.charbuffer))
            self.charbuffer = []

    def buffer_to_int(self,buf):
        i = 0
        while len(buf)>0:
            i = i *256
            i+= buf[0]
            buf = buf[1:]
        return i

    def max_int(self):
        return 256**(self.BufferByteSize)

    def update_buffer(self,buf):
        pass

    def update_int(self,i):
        pass

    def result(self):
        print_nice("ROOT CLASS",magenta,"None")

class SizeTest(RngTest):
    def __init__(self):
        self.charbuffer     = []
        self.BufferByteSize = 1
        self.count = 0

    def update_int(self,i):
        self.count+=1
    def result(self):
        KB = 1024**1  # 1 KiloByte
        MB = 1024**2  # 1 KiloByte
        GB = 1024**3  # 1 KiloByte

        print_status("Input >= 1KB", False, self.count>=KB)
        print_status("Input >= 1MB", False, self.count>=MB)
        print_status("Input >= 1GB", False, self.count>=GB)


class AverageTest(RngTest):
    """The average of random intergers mode 256 will approximate 127.5. It
    wil approximate this value quickly so only a tiny margin of error
    is needed

    """
    def __init__(self):
        self.charbuffer     = []
        self.BufferByteSize = 1
        self.inputCount     = 0
        self.inputSum       = 0

    def update_int(self,i):
        self.inputSum+=i
        self.inputCount+=1

    def result(self):
        weak_error = 0.02 # fraction of max_int()
        hard_error = 0.01 # fraction of max_int()

        expected = 0.5*self.max_int()
        avg = self.inputSum/float(self.inputCount)

        error = abs((avg-expected)/float(self.max_int()))

        print_status("Average: %f"%avg, error<=weak_error,error<=hard_error)


class MeanTest(RngTest):
    """The mean of random intergers mode 256 will approximate 127.5. It is
    suspicious if the mean of uniformly random data mod 256 is less
    than 126 or more than 129.

    """
    def __init__(self):
        self.charbuffer     = []
        self.BufferByteSize = 1
        self.hist = [0 for _ in range(256)]
        self.count = 0

    def update_int(self,i):
        self.hist[i]+=1
        self.count+=1

    def result(self):
        total_ind = 0
        mean = 0
        while mean<256 and total_ind*2<self.count:
            total_ind+=self.hist[mean]
            mean+=1

        print_status("Mean: %i"%mean,mean>=125 and mean<=130,mean>=126 and mean<=129)




class PiTest(RngTest):
    """Randomly pick 24-bit coordinates x,y in [0-1],[0-1]. Calculate ratio
    between point inside and outside unit circle (x^2+y^2=1). If the
    input is properly random this should approximate pi

    """
    def __init__(self):
        self.charbuffer     = []
        self.BufferByteSize = 3
        self.buf = []
        self.InsideCircle = 0
        self.OutsideCircle = 0

    def update_int(self,i):
        self.buf.append(i)
        if len(self.buf)>=2:
            x,y=self.buf[0],self.buf[1]
            self.buf=self.buf[2:]
            if (x**2)+(y**2)<(self.max_int()**2):
                self.InsideCircle+=1
            else:
                self.OutsideCircle+=1

    def result(self):
        if self.InsideCircle + self.OutsideCircle<=0:
            print_status("Pi: NaN",False,False)
            return

        PI = 3.141592653589793

        should_be_pi = (4.0*self.InsideCircle)/(self.InsideCircle + self.OutsideCircle)
        error = abs(PI-should_be_pi)

        print_status("Pi: %f (error: %f)"%(should_be_pi,error),error<0.01,error<0.001)

class EulerTest(RngTest):
    """Pick a uniformly random number in [0,1] and repeat until the sum of
    the numbers picked is >1. You'll on average pick e numbers

    """
    def __init__(self):
        self.charbuffer     = []
        self.BufferByteSize = 7
        self.total_picked = 0
        self.sum_buffer = 0
        self.sums_made = 0

    def update_int(self,i):
        self.total_picked+=1

        self.sum_buffer += i
        if self.sum_buffer >= self.max_int():
            self.sum_buffer = 0
            self.sums_made += 1

    def result(self):
        if self.sums_made<=0:
            print_status("e:  NaN",False,False)
            return
        E = 2.718281828459045
        should_be_e = float(self.total_picked)/float(self.sums_made)
        error = abs(E-should_be_e)
        print_status("e:  %f (error: %f)"%(should_be_e,error),error<0.01,error<0.001)

class LCMCTest(RngTest):
    """Keep track of the amount of times each value is seen. It should not
    me much less common for the least common value to appear compared
    to the most common value. If the result of this test is 0.0, it
    means some values are never occur at all

    """
    def __init__(self):
        self.charbuffer     = []
        self.BufferByteSize = 1
        self.hist           = [0 for _ in range(256)]
        self.hist_xor       = [0 for _ in range(256)]
        self.hist_sum       = [0 for _ in range(256)]
        self.hist_diff      = [0 for _ in range(256)]
        self.hist_prefix    = [[0 for _ in range(256)] for __ in range(256)]
        self.last           = 0
        self.hard_error     = 0.95
        self.weak_error     = 0.90

    def update_int(self,i):
        self.hist[i]+=1
        self.hist_xor[i^self.last]+=1
        self.hist_sum[(i+self.last)%256]+=1
        self.hist_diff[(256+i-self.last)%256]+=1
        self.hist_prefix[self.last][i]+=1
        self.last = i

    def result(self):
        for (style,hist) in [("8-bit",self.hist),
                             ("Xor",self.hist_xor),
                             ("Sum",self.hist_sum),
                             ("Diff",self.hist_diff),]:
            most_common = max(hist)
            least_common = min(hist)
            if most_common>0:
                ml_ratio = float(least_common)/float(most_common)
                print_status("(%06s) lc/mc ratio: %f"%(style,ml_ratio),ml_ratio>=self.weak_error,ml_ratio>=self.hard_error)
            else:
                print_status("(%06s) lc/mc ratio: NaN"%(style),False, False)
        # prefix
        worst = 1.0
        for base in range(256):
            most_common = max(self.hist_prefix[base])
            least_common = min(self.hist_prefix[base])
            if most_common>0:
                ml_ratio = float(least_common)/float(most_common)
                worst=min(worst,ml_ratio)
            else:
                worst = 0.0


        print_status("(Prefix) lc/mc ratio: %f"%worst,worst>=0.1,worst>=0.9)


Tests = [
    SizeTest(),
    AverageTest(),
    MeanTest(),
    PiTest(),
    EulerTest(),
    LCMCTest(),
]
