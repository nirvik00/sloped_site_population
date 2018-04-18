import random
import math

class inp_obj(object):
    def __init__(self,nm,ar,lmin,lmax,wmin,wmax,hmin,hmax,sepmin,sepmax,colr):
        self.name=nm
        self.each_area=ar
        self.l_min=int(lmin)
        self.l_max=int(lmax)
        self.w_min=int(wmin)
        self.w_max=int(wmax)
        self.h_min=int(hmin)
        self.h_max=int(hmax)
        self.sep_min=int(sepmin)
        self.sep_max=int(sepmax)
        self.colr=colr.split("\\")[0]                             
        self.L=random.randint(self.l_min, self.l_max)
        self.W=random.randint(self.w_min, self.w_max)
        self.H=random.randint(self.h_min, self.h_max)
        self.S=random.randint(self.sep_min, self.sep_max)
        
        n=self.each_area/(self.L*self.W*self.H/3)
        m=int(n)
        dec=n-m
        r=int(n)
        if(dec>=0.5):
            r=math.ceil(n)
        else:
            r=math.floor(n)
        self.N=int(r)
        self.attrib=[self.name, self.N, self.L, self.W, self.H, self.S, self.colr]       
    def display_input(self):
        print('name : ',self.name)
        print('A : ',self.each_area)
        print('L : ',self.L)
        print('W : ',self.W)
        print('H : ',self.H)
        print('S : ',self.S)
        print('N : ',self.N)
        print('Color : ',self.colr)
        print('-----------------------------')
    def getL(self):
        return self.L
    def getW(self):
        return self.W
    def getH(self):
        return self.H
    def getN(self):
        return self.N
    def getColr(self):
        return self.colr
    def attributes(self):        
        return self.attrib

