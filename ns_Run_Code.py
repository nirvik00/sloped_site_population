import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter


from ns_abs_cell_obj import abs_cell
from ns_analyze_site_obj import analyze_site
from ns_analyze_input_obj import get_inp


class Cell(object):
    def __init__(self,poly,id,id_):
        self.poly_pts=poly
        self.id=id
        self.poly=None
        self.score=0
        self.base_id=id_
    def get_id(self):
        return self.id
    def gen_poly(self):
        self.poly=rs.AddPolyline(self.poly_pts)
        rs.ObjectLayer(self.poly,'ns_poly')
        return self.poly
    def del_poly(self):
        if(self.poly):
            rs.DeleteObject(self.poly)
    def get_cen(self):
        p0=self.poly_pts[0]
        p2=self.poly_pts[2]
        cen=[(p0[0]+p2[0])/2,(p0[1]+p2[1])/2,0]
        return cen
    def display(self):
        self.t=rs.AddTextDot(str(self.id)+","+str(int(self.score)),self.get_cen())
        rs.ObjectLayer(self.t,'ns_textdot')
    def set_score(self,t):
        self.score=t
    def get_score(self):
        return self.score
    def getL(self):
        p0=self.poly_pts[0]
        p1=self.poly_pts[1]
        di=rs.Distance(p0,p1)
        return di
    def getW(self):
        p0=self.poly_pts[0]
        p3=self.poly_pts[3]
        di=rs.Distance(p0,p3)
        return di
    def pt_in_poly(self,p):
        poly=self.gen_poly()
        t=None
        if(rs.PointInPlanarClosedCurve(p,poly)==0):
            t=False
        else:
            t=True
        rs.DeleteObject(poly)
        return t

class plane_grid(object):
    def __init__(self,poly_,rev_val_,cen_,id_,val_):
        # here the flipped value is used
        self.poly_pts=poly_
        self.cen=cen_
        self.id=id_
        self.grad=rev_val_
        self.ori_grad=val_
    def display(self):
        rs.AddPolyline(self.poly_pts)
        t=rs.AddTextDot(str(self.id)+","+str(int(self.grad)),self.cen)
        #t=rs.AddTextDot(str(int(self.grad)),self.cen)
        rs.ObjectLayer(t,'ns_text_dot')
    def getL(self):
        p0=self.poly_pts[0]
        p1=self.poly_pts[1]
        p2=self.poly_pts[2]
        p3=self.poly_pts[3]
        di=rs.Distance(p0,p1)
        return di
    def getW(self):
        p0=self.poly_pts[0]
        p1=self.poly_pts[1]
        p2=self.poly_pts[2]
        p3=self.poly_pts[3]
        di=rs.Distance(p0,p3)
        return di
    def pt_on_poly(self,p):
        poly=rs.AddPolyline(self.poly_pts)
        t=rs.PointInPlanarClosedCurve(p,poly)
        rs.DeleteObject(poly)
        if(t==0):
            return False
        else:
            return True

class start_proc(object):
    def __init__(self,site_crv,site_srf):
        self.SITE_ON_PLANE=site_crv
        self.SITE_SURFACE=site_srf
        
    def init_gen_building_proc(self, plot_grad):
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
            i.set_flip_value(self.max_grad)
        
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
                    self.ABS_CELL_LI[id].set_occupied(True)
                    used_cell_li.append(id)
                    break
        
    def genGrid(self,site_crv,l, w):
        srf=rs.AddPlanarSrf(site_crv)
        srfUdom=rs.SurfaceDomain(srf,0)
        srfVdom=rs.SurfaceDomain(srf,1)
        umin=srfUdom[0]
        umax=srfUdom[1]
        u=(umax-umin)/l
        #u=(umax-umin)/u_
        ustep=(umax-umin)/u
        vmin=srfVdom[0]
        vmax=srfVdom[1]
        v=(vmax-vmin)/w
        #v=(vmax-vmin)/v_
        vstep=(vmax-vmin)/v
        i=umin
        plane_cell_li=[]
        counter=0
        while i<umax:
            j=umin        
            while j<vmax:
                p0=rs.EvaluateSurface(srf,i,j)
                p1=rs.EvaluateSurface(srf,i+ustep,j)
                p2=rs.EvaluateSurface(srf,i+ustep,j+vstep)
                p3=rs.EvaluateSurface(srf,i,j+vstep)
                t0=rs.PointInPlanarClosedCurve(p0,site_crv)
                t1=rs.PointInPlanarClosedCurve(p1,site_crv)
                t2=rs.PointInPlanarClosedCurve(p2,site_crv)
                t3=rs.PointInPlanarClosedCurve(p3,site_crv)
                if(t0!=0 and t1!=0 and t2!=0 and t3!=0):
                    poly=[p0,p1,p2,p3,p0]
                    
                    cell=Cell(poly,counter)
                    plane_cell_li.append(cell)
                    counter+=1
                j+=vstep
            i+=ustep
        rs.DeleteObject(srf)
        return plane_cell_li
    


lyr1=rs.AddLayer('ns_topo_srf')
lyr2=rs.AddLayer('ns_text_dot')
lyr3=rs.AddLayer('ns_bldg_srf')
lyr4=rs.AddLayer('ns_site_crv')
lyr5=rs.AddLayer('ns_site_srf')
lyr6=rs.AddLayer('ns_flr_crv')
lry7=rs.AddLayer('ns_name_textdot')
lry8=rs.AddLayer('ns_grad_textdot')


rs.LayerVisible('ns_name_textdot',False)
rs.LayerVisible('ns_grad_textdot',False)

site_crv=rs.GetObject('pick plane site')
site_srf=rs.GetObject('pick site surface')
rs.ObjectLayer(site_crv,'ns_site_crv')
rs.ObjectLayer(site_srf,'ns_site_srf')

lyr_poly=rs.AddLayer('ns_poly')
lyr_textdot=rs.AddLayer('ns_textdot')
lyr_path=rs.AddLayer('ns_path')

b=rs.BoundingBox(site_crv)
d1=rs.Distance(b[0],b[1])
d2=rs.Distance(b[2],b[1])

rs.EnableRedraw(False)
"""
a=2
b=a
for i in range(a):
    for j in range(b):
        temp_site_crv=rs.CopyObject(site_crv,[i*(d1+50),j*(d2+50),0])
        temp_site_srf=rs.CopyObject(site_srf,[i*(d1+50),j*(d2+50),0])
        plot_grad=False     # plot textdot showing the grad on srf cells        
        s=start_proc(temp_site_crv, temp_site_srf)
        ##################    construct buildings     ###################
        s.init_gen_building_proc(plot_grad)
        #s.build_blocks_at_distance()   # construct at threshold distance
        s.build_blocks_at_gradient()    # construct on threshold grad
        # not requiresd for now #s.temp_init_build_path(plot_grad)
        #s.build_path()
        if(a==1 and b==1):
            rs.DeleteObjects([temp_site_crv, temp_site_srf])

"""

# for a single generation
s=start_proc(site_crv, site_srf)
plot_grad=True
s.init_gen_building_proc(plot_grad)
#s.build_blocks_at_distance()   # construct at threshold distance
s.build_blocks_at_gradient()    # construct on threshold grad




rs.LayerVisible('ns_site_srf',False)

rs.EnableRedraw(True)