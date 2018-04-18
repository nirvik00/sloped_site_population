import os
from ns_inp_obj import inp_obj

class ns_main_proc_run(object):    
    def __init__(self):
        self.obj_li=[]
        dir=os.getcwd()    
        filename='input.csv'
        with open(filename, "r") as file:
            x=file.readlines()        
        file.close()    
        obj_li=[]
        k=0
        for i in x:
            k+=1
            if(k>1):
                k+=1
                nm=i.split(",")[0]
                if(nm=="" or not nm):
                    break               
                ar=float(i.split(',')[1])
                l_min=float(i.split(',')[2])
                l_max=float(i.split(',')[3])
                w_min=float(i.split(',')[4])
                w_max=float(i.split(',')[5])
                h_min=float(i.split(',')[6])
                h_max=float(i.split(',')[7])
                sep_min=float(i.split(',')[8])
                sep_max=float(i.split(',')[9])
                colr=i.split(',')[10]
                o=inp_obj(nm,ar,l_min,l_max,w_min,w_max,h_min,h_max,sep_min,sep_max,colr)
                self.obj_li.append(o)
    def ret_inp_obj(self):
        return self.obj_li

"""
inp=ns_main_proc_run()
ret=inp.ret_inp_obj()
for i in ret:
    i.display_input()
"""