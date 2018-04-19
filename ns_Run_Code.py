import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter


from ns_abs_cell_obj import abs_cell
from ns_analyze_site_obj import analyze_site
from ns_analyze_input_obj import get_inp

class start_proc(object):
    def __init__(self,site_crv,site_srf, plot_grad):
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
            if(val>self.max_grad):
                self.max_grad=val
            if(val<self.min_grad):
                self.min_grad=val    
        #flip the gradients
        for i in self.ABS_CELL_LI:
            i.flip_value(self.max_grad)
        
        print('min val= %s,  max val= %s'%(self.min_grad,self.max_grad))
        for i in self.ABS_CELL_LI:
            i.gen_srf(self.min_grad,self.max_grad)
        
        self.SORT_LI.sort(key=operator.itemgetter(1))
        
        for i in self.ABS_CELL_LI:
            if(plot_grad==True):
                val=i.plot_val()#PLOT GRADIENTS
            pass
        
        self.THRESHOLD_DISTANCE=0#threshold_distance= distance between buildings
        #called from main process loop - OUTSIDE
        #self.build_blocks_at_distance()
        
        THRESHOLD_GRADIENT=self.max_grad/2
        #called from main process loop - OUTSIDE
        #self.build_blocks_at_gradient()#construct on grad
        
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
            con2=self.THRESHOLD_DISTANCE
            trip=0
            while(id not in used_cell_li and trip<1000):
                id=random.randint(0,len(self.ABS_CELL_LI)-1)
                grad=self.ABS_CELL_LI[id].get_val()
                if(id not in used_cell_li and grad<con1):
                    self.ABS_CELL_LI[id].plot_building(i)
                    used_cell_li.append(id)
                    break
                    
    def build_path(self):
        print('build path')

site_crv=rs.GetObject('pick plane site')
site_srf=rs.GetObject('pick site surface')
b=rs.BoundingBox(site_crv)
d1=rs.Distance(b[0],b[1])
d2=rs.Distance(b[2],b[1])
rs.EnableRedraw(False)
for i in range(1):
    for j in range(1):
        temp_site_crv=rs.CopyObject(site_crv,[i*(d1+50),j*(d2+50),0])
        temp_site_srf=rs.CopyObject(site_srf,[i*(d1+50),j*(d2+50),0])
        plot_grad=True# plot textdot showing the grad on srf cells
        s=start_proc(temp_site_crv, temp_site_srf,plot_grad)
        #s.build_blocks_at_distance() # construct at threshold distance
        #s.build_blocks_at_gradient()# construct on threshold grad
        s.build_path()
rs.EnableRedraw(True)