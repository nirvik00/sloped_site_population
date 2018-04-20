import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter


from ns_abs_cell_obj import abs_cell
from ns_analyze_site_obj import analyze_site
from ns_analyze_input_obj import get_inp

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
                    used_cell_li.append(id)
                    break
    
    def temp_init_build_path(self, plot_grad):
        s=analyze_site(self.SITE_ON_PLANE,self.SITE_SURFACE) #initialize site analysis
        s.genGrid(50,50)
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
            pass
    
    def build_path(self):
        plane_cell_li=[] # poly_pts, flipped_val, cen, id
        for i in self.ABS_CELL_LI:
            v=i.val
            f_v=i.flip_val
            pt=i.get_cen_plane()
            id=i.get_id()
            poly=i.plot_poly_plane()
            plane=plane_grid(poly,f_v,pt,id,v)
            plane_cell_li.append(plane)
            
            
            
        start_poly=rs.AddPolyline(plane_cell_li[0].poly_pts)
        start_pt=plane_cell_li[0].cen
        maxDi=0
        req=0
        counter=-1
        for i in plane_cell_li:
            counter+=1
            i.display()
            di=rs.Distance(start_pt,i.cen)
            if(di>maxDi):
                req=counter
        finish_poly=plane_cell_li[req].poly_pts
        finish_pt=plane_cell_li[req].cen
        rs.AddLine(start_pt,finish_pt)
        
        for i in plane_cell_li:
            cen=i.cen
            di=rs.Distance(start_pt,cen)
            i.grad+=di/15
        
        
        cell_path_li=[]
        cell_path_li.append(plane_cell_li[0])
        main_counter=-1
        while(main_counter<500):
        #i=plane_cell_li[45]
        #if(i):
            main_counter+=1
            #me=i
            me=cell_path_li[-1]
            #print('id',me.id)
            me_cen=me.cen
            p=me_cen[0]
            q=me_cen[1]
            d0=me.getL()
            d1=me.getW()
            ##print('distances',d0,d1)
            le_pt=[me_cen[0]-d0, me_cen[1], 0]#left
            ri_pt=[me_cen[0]+d0, me_cen[1], 0]#right
            up_pt=[me_cen[0], me_cen[1]+d1, 0]#up
            dn_pt=[me_cen[0], me_cen[1]-d1, 0]#down
            li=[]#li
            max_grad=0
            final_cell=None
            for i in plane_cell_li:
                t0=i.pt_on_poly(le_pt)
                t1=i.pt_on_poly(ri_pt)
                t2=i.pt_on_poly(up_pt)
                t3=i.pt_on_poly(dn_pt)
                if(t0==True and i not in cell_path_li):
                    g=i.grad+0
                    if(g>max_grad):
                        max_grad=i.grad
                        final_cell=i
                        li.append(i)
                if(t1==True and i not in cell_path_li):
                    g=i.grad+0
                    if(g>max_grad):
                        max_grad=i.grad
                        final_cell=i
                        li.append(i)
                if(t2==True and i not in cell_path_li):
                    g=i.grad+0
                    if(g>max_grad):
                        max_grad=i.grad
                        final_cell=i
                        li.append(i)
                if(t3==True and i not in cell_path_li):
                    g=i.grad+0
                    if(g>max_grad):
                        max_grad=i.grad
                        final_cell=i
                        li.append(i)
            if(len(li)>0):
                l=rs.AddLine(final_cell.cen,me.cen)
                e=rs.AddLine([0,0,0],[0,0,10])
                rs.ExtrudeCurve(l,e)
                rs.DeleteObject(e)
                cell_path_li.append(final_cell)
                print('last-id',final_cell.id, len(li))

lyr1=rs.AddLayer('ns_topo_srf')
lyr2=rs.AddLayer('ns_text_dot')
lyr3=rs.AddLayer('ns_bldg_srf')
lyr4=rs.AddLayer('ns_site_crv')
lyr5=rs.AddLayer('ns_site_srf')
lyr6=rs.AddLayer('ns_flr_crv')



site_crv=rs.GetObject('pick plane site')
site_srf=rs.GetObject('pick site surface')
rs.ObjectLayer(site_crv,'ns_site_crv')
rs.ObjectLayer(site_srf,'ns_site_srf')

b=rs.BoundingBox(site_crv)
d1=rs.Distance(b[0],b[1])
d2=rs.Distance(b[2],b[1])

rs.EnableRedraw(False)
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
plot_grad=False
s.init_gen_building_proc(plot_grad)
#s.build_blocks_at_distance()   # construct at threshold distance
s.build_blocks_at_gradient()    # construct on threshold grad
plot_grad=False                 # plot textdot showing the grad on srf cells
#s.build_path()
"""
rs.LayerVisible('ns_site_srf',False)

rs.EnableRedraw(True)