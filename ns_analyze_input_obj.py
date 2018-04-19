import rhinoscriptsyntax as rs
import random
import math
from ns_get_input_csv import ns_main_proc_run

class get_inp(object):
    def __init__(self):
        inp=ns_main_proc_run()
        self.inp_obj_li=inp.ret_inp_obj()
        self.full_inp_obj_li=[]
    def get_inp_obj(self):
        for i in self.inp_obj_li:
            i.display_input()
        return self.inp_obj_li
    def get_full_inp_obj_li(self):
        self.full_inp_obj_li=[]
        for i in self.inp_obj_li:
            n=i.getN()
            for j in range(n):
                self.full_inp_obj_li.append(i)
        return self.full_inp_obj_li
    def get_max_l_w(self):
        maxL=0
        maxW=0
        for i in self.full_inp_obj_li:
            L=i.getL()
            W=i.getW()
            if(L>maxL):
                maxL=L
            if(W>maxW):
                maxW=W
        return [maxL, maxW]
