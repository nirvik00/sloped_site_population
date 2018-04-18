import rhinoscriptsyntax as rs
import math
import random
import operator
from operator import itemgetter
from ns_get_input_csv import ns_main_proc_run

class abs_cell(object):
    def __init__(self, v, id_, hi_poly_, low_poly_):
        self.val=v
        self.id=id_
        self.high_poly=hi_poly_
        self.low_poly=low_poly_
        self.srf=None
        self.plot=None
        self.building_srf=None
    def set_val(self,t):
        self.val=t
        print(self.val)
    def get_val(self):
        return self.val
    def get_id(self):
        return self.id
    def get_high_poly(self):
        return self.high_poly
    def get_low_poly(self):
        return low_poly
    def get_cen(self):
        i=self.high_poly
        cen=[(i[0][0]+i[2][0])/2 , (i[0][1]+i[2][1])/2, i[0][2]]
        return cen
    def gen_srf(self):
        high_poly=rs.AddPolyline(self.high_poly)
        low_poly=rs.AddPolyline(self.low_poly)
        self.srf=rs.AddLoftSrf([high_poly,low_poly])
        rs.CapPlanarHoles(self.srf)
        re=int(self.val*15)
        gr=0
        bl=255
        rs.ObjectColor(self.srf,(re,gr,bl))
        rs.DeleteObjects([high_poly, low_poly])
        return self.srf
    def del_srf(self):
        rs.DeleteObject(self.srf)
    def plot_val(self):
        i=self.high_poly
        cen=[(i[0][0]+i[2][0])/2 , (i[0][1]+i[2][1])/2, i[0][2]]
        val=int(self.val)
        id=self.id
        self.plot=rs.AddTextDot(str(id)+","+str(val),cen)
    def del_plot(self):
        try:
            rs.DeleteObject(self.plot)
        except:
            pass
    def plot_building(self,t):
        poly=rs.AddPolyline(self.high_poly)
        cen=rs.CurveAreaCentroid(poly)[0]
        z=cen[2]
        p=rs.CurvePoints(poly)
        vec_ux=p[1][0]-p[0][0]
        vec_uy=p[1][1]-p[0][1]
        nor_ux=vec_ux/(math.sqrt(vec_ux*vec_ux + vec_uy*vec_uy))
        nor_uy=vec_uy/(math.sqrt(vec_ux*vec_ux + vec_uy*vec_uy))
        ux=nor_ux*10
        uy=nor_uy*10
        vec_vx=p[3][0]-p[0][0]
        vec_vy=p[3][1]-p[0][1]
        nor_vx=vec_vx/(math.sqrt(vec_vx*vec_vx + vec_vy*vec_vy))
        nor_vy=vec_vy/(math.sqrt(vec_vx*vec_vx + vec_vy*vec_vy))
        vx=nor_vx*10
        vy=nor_vy*10
        ri=[cen[0]+ux, cen[1]+uy, z]
        ri_up=[ri[0]+vx, ri[1]+vy, z]
        ri_dn=[ri[0]-vx, ri[1]-vy, z]
        le=[cen[0]-ux, cen[1]-uy, z]
        le_up=[le[0]+vx, le[1]+vy, z]
        le_dn=[le[0]-vx, le[1]-vy, z]
        base=rs.AddPolyline([le_up,ri_up,ri_dn,le_dn,le_up])
        pl_srf=rs.AddPlanarSrf(base)
        E=rs.AddLine([0,0,0],[0,0,t.getH()])
        self.building_srf=rs.ExtrudeSurface(pl_srf,E)
        re=int(t.getColr().split("-")[0])
        gr=int(t.getColr().split("-")[1])
        bl=int(t.getColr().split("-")[2])
        rs.ObjectColor(self.building_srf, (re,gr,bl))
        rs.DeleteObjects([pl_srf,E])

class analyze_site(object):
    def __init__(self,site_crv, site_srf):
        self.site_crv=site_crv
        self.site_srf=site_srf        
        self.plane_cell_li=[]        
        self.site_cell_srf=[]        
        self.site_high_cell=[]
        self.site_low_cell=[]        
        self.cell_slope_val=[]
        self.abs_cell_li=[]
    def genGrid(self, l, w):
        srf=rs.AddPlanarSrf(self.site_crv)
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
        self.plane_cell_li=[]
        while i<umax:
            j=umin
            while j<vmax:
                p0=rs.EvaluateSurface(srf,i,j)
                p1=rs.EvaluateSurface(srf,i+ustep,j)
                p2=rs.EvaluateSurface(srf,i+ustep,j+vstep)
                p3=rs.EvaluateSurface(srf,i,j+vstep)
                t0=rs.PointInPlanarClosedCurve(p0,self.site_crv)
                t1=rs.PointInPlanarClosedCurve(p1,self.site_crv)
                t2=rs.PointInPlanarClosedCurve(p2,self.site_crv)
                t3=rs.PointInPlanarClosedCurve(p3,self.site_crv)
                if(t0!=0 and t1!=0 and t2!=0 and t3!=0):
                    self.plane_cell_li.append([p0,p1,p2,p3])
                j+=vstep
            i+=ustep
        rs.DeleteObject(srf)
    def project_on_site(self):
        self.site_high_cell=[]
        self.site_low_cell=[]
        try:
            rs.DeleteObjects(self.site_cell_srf)
        except:
            pass
        srf_poly_raw=[]
        counter=-1
        for i in self.plane_cell_li:
            counter+=1
            a=[i[0][0],i[0][1],i[0][2]]
            b=[i[1][0],i[1][1],i[0][2]]
            c=[i[2][0],i[2][1],i[2][2]]
            d=[i[3][0],i[3][1],i[3][2]]
            a_=[i[0][0],i[0][1],i[0][2]-10000]
            b_=[i[1][0],i[1][1],i[0][2]-10000]
            c_=[i[2][0],i[2][1],i[2][2]-10000]
            d_=[i[3][0],i[3][1],i[3][2]-10000]
            l0=rs.AddLine(a,a_)
            l1=rs.AddLine(b,b_)
            l2=rs.AddLine(c,c_)
            l3=rs.AddLine(d,d_)
            p=rs.CurveSurfaceIntersection(l0,self.site_srf)[0][1]
            q=rs.CurveSurfaceIntersection(l1,self.site_srf)[0][1]
            r=rs.CurveSurfaceIntersection(l2,self.site_srf)[0][1]
            s=rs.CurveSurfaceIntersection(l3,self.site_srf)[0][1]
            rs.DeleteObjects([l0,l1,l2,l3])
            p_=[p[0],p[1],p[2]]
            q_=[q[0],q[1],q[2]]
            r_=[r[0],q[1],r[2]]
            s_=[s[0],s[1],s[2]]
            srf_poly_raw.append([p_,q_,r_,s_])
            hts=[p[2],q[2],r[2],s[2]]
            hts.sort()
            highZ=hts[len(hts)-1]
            lowZ=hts[0]
            p00=[p[0],p[1],highZ]
            q00=[q[0],q[1],highZ]
            r00=[r[0],r[1],highZ]
            s00=[s[0],s[1],highZ]
            p01=[p[0],p[1],lowZ]
            q01=[q[0],q[1],lowZ]
            r01=[r[0],r[1],lowZ]
            s01=[s[0],s[1],lowZ]            
            # srf is added to cell
            self.site_high_cell.append([p00,q00,r00,s00,p00])
            high_cell=[p00,q00,r00,s00,p00]
            self.site_low_cell.append([p01,q01,r01,s01,p01])            
            low_cell=[p01,q01,r01,s01,p01]
            #high_poly=rs.AddPolyline([p00,q00,r00,s00,p00])
            #low_poly=rs.AddPolyline([p01,q01,r01,s01,p01])
            #srf=rs.AddLoftSrf([high_poly,low_poly])
            #rs.CapPlanarHoles(srf)        
            #self.site_cell_srf.append(srf)
            #rs.DeleteObjects([high_poly,low_poly])
            """ srf is added to cell """            
            this_cell=abs_cell(0, counter, high_cell, low_cell)
            self.abs_cell_li.append(this_cell)
        counter=-1
        for i in srf_poly_raw:
            counter+=1
            p0=i[0]
            p1=i[1]
            p2=i[2]
            p3=i[3]
            dz0=math.fabs(i[3][2]-i[0][2])
            dz1=math.fabs(i[2][2]-i[0][2])
            dz2=math.fabs(i[1][2]-i[0][2])
            #dz=round((dz0+dz1+dz2),2)
            dz=(dz0+dz1+dz2)
            self.cell_slope_val.append(dz)
            self.abs_cell_li[counter].set_val(dz)
    def get_abs_cell_li(self):
        return self.abs_cell_li

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


SITE_ON_PLANE=rs.GetObject('pick plane site')
SITE_SURFACE=rs.GetObject('pick site surface')

rs.EnableRedraw(False)
inp=get_inp()
full_inp_obj_li=inp.get_full_inp_obj_li()
max_LW=inp.get_max_l_w()
print(max_LW)
for i in full_inp_obj_li:
    #print(i.display_input())
    pass
    
s=analyze_site(SITE_ON_PLANE,SITE_SURFACE)
s.genGrid(max_LW[0], max_LW[1])
s.project_on_site()

abs_cell_li=s.get_abs_cell_li()
li=[]
for i in abs_cell_li:
    id=i.get_id()
    val=i.get_val()
    li.append([id,val])
    #i.plot_val()
    i.gen_srf()
li.sort(key=operator.itemgetter(1))

counter=-1
prev_id=-1
used_cen_li=[]
prev_cen=[]
for i in full_inp_obj_li:
    counter+=1
    this_id=li[counter][0]
    this_cen=abs_cell_li[this_id].get_cen()
    if(prev_id==-1):
        abs_cell_li[this_id].plot_building(i)
        used_cen_li.append(this_cen)        
        prev_id=this_id
    else:
        sum=0
        for j in used_cen_li:
            a=this_cen
            b=j
            di=math.sqrt((a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1]) + (a[2]-b[2])*(a[2]-b[2]))
            if(di>50):
                abs_cell_li[this_id].plot_building(i)
                sum+=1
        if(sum==0):
            prev_id=this_id
            used_cen_li.append(this_cen)        


rs.EnableRedraw(True)
