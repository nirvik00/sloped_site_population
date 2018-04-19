import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter


from ns_abs_cell_obj import abs_cell
from ns_analyze_site_obj import analyze_site
from ns_analyze_input_obj import get_inp

class start_proc(object):
    def __init__(self,site_crv,site_srf):
        self.SITE_ON_PLANE=site_crv
        self.SITE_SURFACE=site_srf
        
        inp=get_inp() # call - main csv process and intialize and get the input objects
        self.FULL_INP_OBJ_LI=inp.get_full_inp_obj_li() # expanded input objects 
        max_LW=inp.get_max_l_w()
        
        s=analyze_site(self.SITE_ON_PLANE,self.SITE_SURFACE) #initialize site analysis
        s.genGrid(max_LW[0], max_LW[1])
        s.project_on_site()
        
        self.ABS_CELL_LI=s.get_abs_cell_li() #initialize abstract cell gradient class
        self.SORT_LI=[]  #initialize site analysis
        self.max_grad=0
        self.min_grad=100
        for i in self.ABS_CELL_LI:
            id=i.get_id()
            val=i.get_val()
            self.SORT_LI.append([id,val])
            #val=i.plot_val()
            if(val>self.max_grad):
                self.max_grad=val
            if(val<self.min_grad):
                self.min_grad=val    
        
        print('min val= %s,  max val= %s'%(self.min_grad,self.max_grad))
        for i in self.ABS_CELL_LI:
            i.gen_srf(self.min_grad,self.max_grad)
        
        self.SORT_LI.sort(key=operator.itemgetter(1))
        
        for i in self.ABS_CELL_LI:
            #val=i.plot_val()#PLOT GRADIENTS
            pass
        
        self.THRESHOLD_DISTANCE=50#threshold_distance= distance between buildings
        self.build_blocks_at_distance()
        
        THRESHOLD_GRADIENT=self.max_grad/2
        #build_blocks_at_gradient(SORT_LI,FULL_INP_OBJ_LI,ABS_CELL_LI)#construct on grad
        
    def build_blocks_at_distance(self):
        counter=-1
        plot_counter=0
        used_cen_li=[]
        for i in self.SORT_LI:
            # full_inp_obj_li = list of [ 1 object with L,W,H,S,Colr ]
            # abs_cell_li = list of [ 1 cell with id,val,high_poly,low_poly,cen,srf ]
            # li= list of [ id, val of abs_cell_li ]
            counter+=1
            plot_bldg_sum=0
            if (plot_counter<len(self.FULL_INP_OBJ_LI)):
                inp_obj=self.FULL_INP_OBJ_LI[plot_counter]
                id=i[0]
                this_cen=self.ABS_CELL_LI[id].get_cen()
                for j in used_cen_li:
                    di=rs.Distance(j,this_cen)
                    if(di<self.THRESHOLD_DISTANCE):
                        plot_bldg_sum+=1
                if(plot_bldg_sum==0):
                    self.ABS_CELL_LI[id].plot_building(inp_obj)
                    used_cen_li.append(this_cen)
                    plot_counter+=1
            else:
                break

    def build_blocks_at_gradient(self):
        counter=-1
        plot_counter=0
        used_cell_li=[]
        for i in self.FULL_INP_OBJ_LI:
            id=random.randint(0,len(self.ABS_CELL_LI)-1)
            con1=self.max_grad/2
            while(id in used_cell_li):
                id=random.randint(0,len(self.ABS_CELL_LI)-1)
                used_cell_li.append(id)

site_crv=rs.GetObject('pick plane site')
site_srf=rs.GetObject('pick site surface')

rs.EnableRedraw(False)
start_proc(site_crv, site_srf)
rs.EnableRedraw(True)