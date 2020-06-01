import mpmath
from mpmath import mpf
from mpmath import ln
from mpmath import findroot
from scipy  import integrate
import random

mpmath.mp.prec +=100
mpmath.mp.dps = 100

class Weibull:

    def __init__(self, shape=1, scale=1, location=0):
        self.shape = float(shape)
        self.scale = float(scale)
        self.location = float(location)

    def draw(self):
        return random.weibullvariate(self.scale, self.shape)+self.location

class SSD_fail:

    def __init__(self):
        self.randomlist = []
        #print "asdasdas"
    def failh(self,x):
        if x<=20:
            x=x/1.17647+3
            a1 = mpmath.power(x, 1)
            a2 = mpmath.power(x, 2)
            a3 = mpmath.power(x, 3)
            a4 = mpmath.power(x, 4)
            a5 = mpmath.power(x, 5)
            a6 = mpmath.power(x, 6)
            y = -0.0002823 * a6 + 0.02235 * a5 - 0.7001 * a4 + 10.91 * a3 - 87.08 * a2 + 332.9 * a1 - 458.06
            y = y / 100
            return y
        else:
            y=0.847399993557042
            return y
    def failfun(self,t):
        if t<=20:
            pdf=integrate.quad(lambda x:self.failh(x),0,t)
            result=self.failh(t)*mpmath.exp(0-pdf[0])
            return result
        else:
            pdf=integrate.quad(lambda x:self.failh(x),0,20)
            result=self.failh(t)*mpmath.exp(0-pdf[0]-(t-20)*0.847399993557042)
            return result

    def drawx(self):
        tmp = 0.
        x = 0.
        y = 0.
        while True:
            x = random.uniform(0, 20)
            y = random.uniform(0, 0.2)
            if y < self.failfun(x):
                tmp = x
                break
        tmp = tmp * 3753
        #print "ssd", tmp
        return tmp

    def drawlist(self):
        for i in range(10000):
            #print i
            self.randomlist.append(self.drawx())
        #print self.randomlist

    def draw(self):
        #num =random.randint(0, 9999)
        num = self.drawx()
        return num

class test:
    def cout(self):
        ssd_disk = SSD_fail()
        print ssd_disk.draw()
        disk = Weibull(shape=1.2, scale=87600, location=0.01)
        print disk.draw()
