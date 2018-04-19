import rhinoscriptsyntax as rs
import math
import random
from ns_abs_cell_obj import abs_cell

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
