import rhinoscriptsyntax as rs
import math
import random
import operator 
from operator import itemgetter

class Cell(object):
    def __init__(self,poly,id):
        self.poly_pts=poly
        self.id=id
        self.poly=None
        self.score=0
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
        self.t=rs.AddTextDot(self.id,self.get_cen())
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
        
def genGrid(site_crv,l, w):
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

def initPath(cells):
    start_cen=cells[0].get_cen()
    max_di=0
    max_id=0
    for i in cells:
        i.gen_poly()
        cen=i.get_cen()
        di=rs.Distance(start_cen,cen)
        id=i.id
        #i.display()
        #print(id, di)
        if(di>max_di):
            max_di=di
            max_id=id
    #print(max_id)
    cells[max_id].set_score(100)
    rs.AddLine(cells[max_id].get_cen(),start_cen)

def buildPath(cells):
    path=[]
    path.append(cells[0])
    counter=0
    while(counter<10):
        counter+=1
        i=path[-1]
        me=i.get_cen()
        meL=i.getL()
        meW=i.getW()
        me_score=i.get_score()
        ri=[me[0]+meL,me[1],0] #ri
        le=[me[0]-meL,me[1],0] #le
        up=[me[0],me[1]+meW,0] #up
        dn=[me[0],me[1]-meW,0] #dn
        max_score=0
        score_li=[] # [ cell, score ]
        for j in cells:
            if(j not in path):
                this_score=j.get_score()
                if(j.pt_in_poly(le)==True):
                    score_li.append([j,this_score])
                if(j.pt_in_poly(ri)==True):
                    score_li.append([j,this_score])
                if(j.pt_in_poly(up)==True):
                    score_li.append([j,this_score])
                if(j.pt_in_poly(dn)==True):
                    score_li.append([j,this_score])
        score_li.sort(key=itemgetter(1))
        print('\n\n---------')
        if(len(score_li)>0):
            for j in score_li:
                print('got score= %s , this_id= %s, req_id= %s'%(j[1], i.id, j[0].id))
            req_cell=score_li[-1][0]
            next=req_cell.get_cen()
            print('acceted id %s'%(req_cell.id))
            L=rs.AddLine(me,next)
            rs.ObjectLayer(L,'ns_path')
            path.append(req_cell)

def update_matrix(cells,recursion_counter):
    for i in cells:
        me=i.get_cen()
        meL=i.getL()
        meW=i.getW()
        me_score=i.get_score()
        ri=[me[0]+meL,me[1],0] #ri
        le=[me[0]-meL,me[1],0] #le
        up=[me[0],me[1]+meW,0] #up
        dn=[me[0],me[1]-meW,0] #dn
        max_score=0
        score_li=[]
        for j in cells:
            this_score=j.get_score()
            this=j.get_cen()
            di=rs.Distance(this,me)
            if(j.pt_in_poly(le)==True):
                score_li.append(this_score)
            if(j.pt_in_poly(ri)==True):
                score_li.append(this_score)
            if(j.pt_in_poly(up)==True):
                score_li.append(this_score)
            if(j.pt_in_poly(dn)==True):
                score_li.append(this_score)
        for j in score_li:
            if(j>max_score):
                max_score=j
        if(max_score>i.get_score()):
            i.set_score(max_score*0.85)
    sum=0
    for i in cells:
        me=i.get_cen()
        #rs.AddTextDot(i.get_score(),me)
        if(me==0):
            sum+=1
    if(recursion_counter<20 and sum<10):
        recursion_counter+=1
        #print('recursion')
        update_matrix(cells,recursion_counter)
    else:
        for i in cells:
            me=i.get_cen()
            i.display()




rs.EnableRedraw(False)


lyr_poly=rs.AddLayer('ns_poly')
lyr_textdot=rs.AddLayer('ns_textdot')
lyr_path=rs.AddLayer('ns_path')

SITE_CRV=rs.GetObject('pick site curve')
CELL_LI=genGrid(SITE_CRV,50,50)
initPath(CELL_LI)
update_matrix(CELL_LI,0)
buildPath(CELL_LI)


rs.EnableRedraw(True)