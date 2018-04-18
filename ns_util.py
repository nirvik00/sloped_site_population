import rhinoscriptsyntax as rs
import math
import operator
from operator import itemgetter
import random
import os
from ns_inp_obj import inp_obj  

def srfGrid(site_crv,site_crv_neg,u,v):
    bldg_sites=[]
    poly_sites=[]
    srf=rs.AddPlanarSrf(site_crv)
    srfUdom=rs.SurfaceDomain(srf,0)
    srfVdom=rs.SurfaceDomain(srf,1)
    umin=srfUdom[0]
    umax=srfUdom[1]
    vmin=srfVdom[0]
    vmax=srfVdom[1]
    #ustep=(umax-umin)/u
    ustep=u
    #vstep=(vmax-vmin)/v
    vstep=v
    i=umin
    while i<umax:
        j=vmin
        while j<vmax:
            p0=rs.EvaluateSurface(srf, i,j)
            p1=rs.EvaluateSurface(srf, i+ustep,j)
            p2=rs.EvaluateSurface(srf, i+ustep,j+vstep)
            p3=rs.EvaluateSurface(srf, i,j+vstep)
            sum=0
            try:
                for k in site_crv_neg:
                    t0=rs.PointInPlanarClosedCurve(p0,k)
                    t1=rs.PointInPlanarClosedCurve(p1,k)
                    t2=rs.PointInPlanarClosedCurve(p2,k)
                    t3=rs.PointInPlanarClosedCurve(p3,k)
                    if(t0!=0 or t2!=0 or t3!=0 or t1!=0):
                        sum+=1
            except:
                pass
            t0=rs.PointInPlanarClosedCurve(p0,site_crv)
            t1=rs.PointInPlanarClosedCurve(p1,site_crv)
            t2=rs.PointInPlanarClosedCurve(p2,site_crv)
            t3=rs.PointInPlanarClosedCurve(p3,site_crv)
            if(t0==0 or t2==0 or t3==0 or t1==0):
                sum+=1
            if(sum==0):
                #poly=rs.AddPolyline([p0,p1,p2,p3,p0])
                #rs.ObjectLayer(poly,"ns_output_poly")
                #poly_pts=[p0,p1,p2,p3,p0]
                #poly_sites.append(poly)
                x0=p0[0]
                x2=p2[0]
                y0=p0[1]
                y2=p2[1]
                r_pt=[(x0+x2)/2,(y0+y2)/2,0]
                bldg_sites.append(r_pt)
            j+=vstep
        i+=ustep
    rs.DeleteObject(srf)
    return bldg_sites

def genMassFrom_Cp_lw(nm, p,l,w,h,c, ht_con):
    L=float(l)/2
    W=float(w)/2
    num_flrs=int(h/3)
    #"""
    C=c.split("-")
    re=int(C[0])
    gr=int(C[1])
    bl=int(C[2])
    #"""
    #print("L = ",L)
    #print("W = ",W)
    a=[p[0]-L, p[1]-W, 0]
    b=[p[0]+L, p[1]-W, 0]
    c=[p[0]+L, p[1]+W, 0]
    d=[p[0]-L, p[1]+W, 0]    
    this_pts=[a,b,c,d,a]
    poly=rs.AddPolyline(this_pts)
    rs.ObjectLayer(poly,"ns_checks")
    min_ht=getHtConstraintsData(ht_con,poly)
    #print(min_ht, h)    
    if(float(min_ht)<float(h)):
        num_flrs=int(min_ht/3)
    final_ar_check=0
    flr_li=[]
    for i in range(0,num_flrs,1):
        flr=rs.CopyObject(poly, [0,0,i*3])
        rs.ObjectLayer(flr,"ns_flr_crv")
        flr_li.append(flr)
        final_ar_check+=(rs.CurveArea(flr)[0])
    """
    srf=rs.AddLoftSrf(flr_li)
    rs.CapPlanarHoles(srf)
    rs.ObjectColor(srf, (re,gr, bl))
    rs.ObjectLayer(srf, "ns_srf")
    return [flr_li, srf, final_ar_check]
    """
    rs.DeleteObject(poly)
    return [flr_li, final_ar_check]

def genExtPoly(site_crv,p,l,w,s,poly_li,neg_poly_li):
    a=[p[0]-l/2-s/2, p[1]-w/2-s/2, 0]
    b=[p[0]+l/2+s/2, p[1]-w/2-s/2, 0]
    c=[p[0]+l/2+s/2, p[1]+w/2+s/2, 0]
    d=[p[0]-l/2-s/2, p[1]+w/2+s/2, 0]    
    this_pts=[a,b,c,d,a]
    t0=rs.PointInPlanarClosedCurve(a,site_crv)
    t1=rs.PointInPlanarClosedCurve(b,site_crv)
    t2=rs.PointInPlanarClosedCurve(c,site_crv)
    t3=rs.PointInPlanarClosedCurve(d,site_crv)
    sum=0
    if(t0==0 or t2==0 or t3==0 or t1==0):
        sum+=1
    if(sum==0):
        sumX=0
        if(poly_li and len(poly_li)>0):
            for i in poly_li:
                tx=checkPoly(this_pts,i)
                if(tx==False):
                    sumX+=1
        if(neg_poly_li and len(neg_poly_li)>0):
            for i in neg_poly_li:
                tx=checkPoly(this_pts,i)
                if(tx==False):
                    sumX+=1
        if(sumX==0):
            poly=rs.AddPolyline(this_pts)
            #poly=this_pts
            return poly
        else:
            return None
    else:
        return None

def checkPoly(pts,poly):
    sum=0
    for i in pts:
        m=rs.PointInPlanarClosedCurve(i,poly)
        if(m!=0):
            sum+=1
    poly2=rs.AddPolyline(pts)
    pts2=rs.CurvePoints(poly)
    for i in pts2:
        m=rs.PointInPlanarClosedCurve(i,poly2)
        if(m!=0):
            sum+=1
    intx=rs.CurveCurveIntersection(poly,poly2)
    rs.DeleteObject(poly2)
    if(sum>0 or intx):
        return False
    else:
        return True

def constructTopoPoly(srf,poly):
    if(srf ==None):
        return
    poly_pts=rs.CurvePoints(poly)
    pts=poly_pts
    req_pts=[]
    req_pts_dup=[]
    for i in pts:
        pt2=rs.AddPoint([i[0],i[1],i[2]-1000])
        L=rs.AddLine(i,pt2)
        intx=rs.CurveSurfaceIntersection(L,srf)
        if(intx and len(intx)>0):
            pt=[intx[0][1][0],intx[0][1][1],intx[0][1][2]]
            rs.DeleteObject(L)
            rs.DeleteObject(pt2)
            req_pts.append([pt[0],pt[1],pt[2]])
            req_pts_dup.append([pt[0],pt[1],pt[2]])
    req_pts_dup.sort(key=operator.itemgetter(2))
    max_z=req_pts_dup[len(req_pts_dup)-1][2]# higher
    min_z=req_pts_dup[0][2]# higher
    high_pts=[]
    low_pts=[]
    for i in req_pts:
        high_pt=[i[0],i[1],max_z]
        high_pts.append(high_pt)
        low_pt=[i[0],i[1],min_z]
        low_pts.append(low_pt)
    high_pl=rs.AddPolyline(high_pts)
    low_pl=rs.AddPolyline(low_pts)
    this_srf=rs.AddLoftSrf([high_pl,low_pl])
    rs.DeleteObjects([low_pl,poly])
    rs.CapPlanarHoles(this_srf)
    return high_pl

def getHtConstraintsData(ht_constraint_srfs, check_for_poly):
    j=check_for_poly
    ht_constraint=1000000
    min_ht=ht_constraint
    try:
        for h_ite in ht_constraint_srfs:
            bhtc=rs.BoundingBox(h_ite)
            poly_htc=rs.AddPolyline([bhtc[0],bhtc[1],bhtc[2],bhtc[3],bhtc[0]])
            int_htcon_sum=0 #if this remains 0 => no change
            for poly_pt in rs.CurvePoints(j):
                t=rs.PointInPlanarClosedCurve(poly_pt,poly_htc)
                if(t==1): #point is inside the poly then not correct
                    int_htcon_sum+=1
            for bound_pt in rs.CurvePoints(poly_htc):
                t=rs.PointInPlanarClosedCurve(bound_pt,j)
                if(t==1): #point is inside the poly then not correct
                    int_htcon_sum+=1
            intx1=rs.CurveCurveIntersection(poly_htc,j)
            if(intx1 and len(intx1)>0):
                int_htcon_sum+=1
            if(int_htcon_sum>0):
                ht_constraint=rs.Distance(bhtc[0],bhtc[4])
                if(ht_constraint<min_ht):
                    min_ht=ht_constraint
            else:
                pass
            rs.DeleteObject(poly_htc)
    except:
        pass
    return min_ht

