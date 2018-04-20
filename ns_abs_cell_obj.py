import rhinoscriptsyntax as rs
import math
import random

class abs_cell(object):
    def __init__(self, v, id_, hi_poly_, low_poly_):
        self.val=v
        self.flip_val=0
        self.id=id_
        self.high_poly=hi_poly_
        self.low_poly=low_poly_
        self.srf=None
        self.plot=None
        self.building_srf=None
        self.occupied=False
    def set_val(self,t):
        self.val=t
        #print(self.val)
    def get_val(self):
        return val
    def set_flip_value(self,max):
        self.flip_val=max-self.val    
    def get_flip_value(self,max):
        return self.flip_val
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
    def get_cen_plane(self):
        i=self.high_poly
        cen=[(i[0][0]+i[2][0])/2 , (i[0][1]+i[2][1])/2, 0]
        return cen
    def get_right_dim(self):
        i=self.high_poly
        di=math.fabs(i[0][0]-i[1][0])
        return di
    def get_up_dim(self):
        i=self.high_poly
        di=math.fabs(i[3][0]-i[0][0])
        return di
    def gen_srf(self, min_grad, max_grad):
        fac=255/max_grad
        high_poly=rs.AddPolyline(self.high_poly)
        low_poly=rs.AddPolyline(self.low_poly)
        self.srf=rs.AddLoftSrf([high_poly,low_poly])
        rs.CapPlanarHoles(self.srf)
        re=int(self.val*fac)
        gr=0
        bl=255
        rs.ObjectColor(self.srf,(re,gr,bl))
        rs.DeleteObjects([high_poly, low_poly])
        rs.ObjectLayer(self.srf,'ns_topo_srf')
        return self.srf
    def del_srf(self):
        rs.DeleteObject(self.srf)
    def plot_val(self):
        i=self.high_poly
        cen=[(i[0][0]+i[2][0])/2 , (i[0][1]+i[2][1])/2, i[0][2]]
        val=int(self.val)
        id=self.id
        self.plot=rs.AddTextDot("v= "+str(val)+", r="+str(int(self.flip_val)),cen)
        return self.val
    def plot_val_plane(self):
        i=self.high_poly
        cen=[(i[0][0]+i[2][0])/2 , (i[0][1]+i[2][1])/2, 0]
        val=int(self.val)
        id=self.id
        self.plot=rs.AddTextDot("v= "+str(val)+", r="+str(int(self.flip_val)),cen)
        return self.val
    def plot_poly_plane(self):
        pts=[]
        for i in self.high_poly:
            p=[i[0],i[1],0]
            pts.append(p)
        return pts
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
        rs.ObjectLayer(self.building_srf,'ns_bldg_srf')
        re=int(t.getColr().split("-")[0])
        gr=int(t.getColr().split("-")[1])
        bl=int(t.getColr().split("-")[2])
        rs.ObjectColor(self.building_srf, (re,gr,bl))
        for i in range(0,t.getH(),3):
            flr=rs.CopyObject(base,[0,0,i])
            rs.ObjectLayer(flr,'ns_flr_crv')
        rs.DeleteObjects([pl_srf,E,base])
    def get_occupied(self):
        return self.occupied
    def set_occupied(self, t):
        self.occupied=t

