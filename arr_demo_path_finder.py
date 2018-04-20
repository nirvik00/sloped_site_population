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

def gen(M,N):
    row=[]
    for i in range(0,M):
        row.append(i)
        row[i]=[]
        for j in range(0,N):
            row[i].append(0)
    row[M-1][N-1]=100
    #print('initial matrix')
    for i in row:
        #print(i)
        pass
    #print('\n-----------------------------\n\n')
    return row

def update_matrix(arr,M,N,recursion_counter):
    for i in range(M):
        for j in range(N):
            this=arr[i][j]
            max=[]
            #up
            if(i<M-1):
                up=arr[i+1][j]
                max.append(up)
            #dn
            if(i>0):
                dn=arr[i-1][j]
                max.append(dn)
            #ri
            if(j<N-1):
                ri=arr[i][j+1]
                max.append(ri)
            #le
            if(j>0):
                le=arr[i][j-1]
                max.append(le)            
            max.sort()
            if(max[-1]>this):
                arr[i][j]=max[-1]*0.8
    sum=0
    for i in arr:
        for j in i:
            if(j==0):
                sum+=1
    if(sum>1 and recursion_counter<100):
        recursion_counter+=1
        update_matrix(arr,M,N,recursion_counter)
    else:
        #print('\n\nupdate\n-------------\n')
        for i in arr:
            #print(i)
            pass
    return arr

def gen_path(arr,M,N):
    # first index=number of columns
    # second index=number of rows
    path=[]
    path.append([0,0])
    counter=-1
    while(counter<500):
        counter+=1
        i=path[-1][0]
        j=path[-1][1]
        me=arr[i][j]
        max=[]
        id=[0,0]
        #up
        if(i<M-1):
            up=arr[i+1][j]
            id=[i+1,j]
            #print('up',up, i+1,j)
            if(id not in path):
                max.append([up,id])
        #dn
        if(i>0):
            dn=arr[i-1][j]
            id=[i-1,j]
            #print('dn',dn,i-1,j)
            if(id not in path):
                max.append([dn,id])
        #ri
        if(j<N-1):
            ri=arr[i][j+1]
            id=[i,j+1]
            #print('ri',ri,i,j+1)
            if(id not in path):
                max.append([ri,id])
        #le
        if(j>0):
            le=arr[i][j-1]
            id=[i,j-1]
            #print('le',le,i,j-1)
            if(id not in path):
                max.append([le,id])            
        max.sort(key=operator.itemgetter(0))
        req=max[-1][1]
        a=req[0]
        b=req[1]
        #path.append([a,b])
        #print('max',max)
        #print('indices : ',a,b)
        path.append([a,b])
        if(a==M-1 and b==N-1):
            break
    for i in path:
        print(i)
        
        
        
def place_arr_curve(site,Le,Wi):
    rs.EnableRedraw(False)
    b=rs.BoundingBox(site)
    L=math.fabs(b[0][0]-b[1][0])
    W=math.fabs(b[0][1]-b[3][1])
    row_num=int(L/Le)
    col_num=int(W/Wi)
    rs.MessageBox(str(row_num)+","+str(col_num))
    rs.EnableRedraw(True)
    return [row_num,col_num]

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
    arr=[]
    row_counter=-1
    col_counter=-1
    while i<umax:
        row_counter+=1
        j=umin        
        arr[row_counter]=[]
        while j<vmax:
            col_counter+=1
            p0=rs.EvaluateSurface(srf,i,j)
            p1=rs.EvaluateSurface(srf,i+ustep,j)
            p2=rs.EvaluateSurface(srf,i+ustep,j+vstep)
            p3=rs.EvaluateSurface(srf,i,j+vstep)
            t0=rs.PointInPlanarClosedCurve(p0,site_crv)
            t1=rs.PointInPlanarClosedCurve(p1,site_crv)
            t2=rs.PointInPlanarClosedCurve(p2,site_crv)
            t3=rs.PointInPlanarClosedCurve(p3,site_crv)
            if(t0!=0 and t1!=0 and t2!=0 and t3!=0):
                arr[row_counter][col_counter]=[i,j]
                poly=[p0,p1,p2,p3,p0]
                cell=Cell(poly,counter)
                plane_cell_li.append(cell)
                counter+=1
            j+=vstep
        i+=ustep
    rs.DeleteObject(srf)
    return plane_cell_li

SITE=rs.GetObject("pick curve")
Le=50
Wi=25
NUM_LI=place_arr_curve(SITE,Le,Wi)
#row and col are reversed
m=NUM_LI[1]
n=NUM_LI[0]
ARR=gen(m,n)
F_ARR=update_matrix(ARR,m,n,0)
gen_path(F_ARR,m,n)