"""Illustrative procedural 3D geometry, NOT reconstructed CAD or photogrammetry."""
import math
import plotly.graph_objects as go

def cylinder(fig, center, radius, length, axis='x', color='#46b8d8', label=''):
    cx,cy,cz=center; a=[2*math.pi*i/20 for i in range(21)]
    xx=[];yy=[];zz=[]
    for t in (0,length):
        for ang in a:
            u=radius*math.cos(ang); v=radius*math.sin(ang)
            if axis=='x': xx.append(cx+t);yy.append(cy+u);zz.append(cz+v)
            else: xx.append(cx+u);yy.append(cy+v);zz.append(cz+t)
    n=len(a); i=[];j=[];k=[]
    for q in range(n-1):
        i.extend([q,q+1]);j.extend([q+1,n+q+1]);k.extend([n+q,n+q])
    fig.add_trace(go.Mesh3d(x=xx,y=yy,z=zz,i=i,j=j,k=k,color=color,opacity=.9,name=label,hovertext=label,hoverinfo='text',showscale=False))

def cuboid(fig,x,y,z,dx,dy,dz,color,label):
    xs=[x,x+dx,x+dx,x,x,x+dx,x+dx,x];ys=[y,y,y+dy,y+dy,y,y,y+dy,y+dy];zs=[z,z,z,z,z+dz,z+dz,z+dz,z+dz]
    fig.add_trace(go.Mesh3d(x=xs,y=ys,z=zs,alphahull=0,color=color,opacity=.8,name=label,hovertext=label,hoverinfo='text',showscale=False))

def model(machine, highlight=None):
    f=go.Figure(); blue='#2ca5c9'; amber='#f59e0b'; steel='#6b819b'
    def c(name): return amber if highlight and name.lower() in highlight.lower() else blue
    if machine=='Motor elétrico':
        cylinder(f,(0,0,1),.78,2.7,color=c('Enrolamentos'),label='Carcaça / enrolamentos')
        cylinder(f,(-.6,0,1),.18,3.8,color=steel,label='Eixo')
        cylinder(f,(.15,0,1),.84,.25,color=c('Rolamentos'),label='Rolamentos')
        cylinder(f,(2.5,0,1),.88,.25,color=c('Ventilador'),label='Ventilador')
        cuboid(f,0,-.8,0,2.5,1.6,.25,steel,'Base')
    elif machine=='Bomba centrífuga':
        cylinder(f,(0,0,1),.7,1.2,color=c('Rotor'),label='Corpo da bomba / rotor')
        cylinder(f,(1.4,0,1),.55,2.0,color=c('Motor'),label='Motor')
        cylinder(f,(-.9,0,1),.28,1.1,color=steel,label='Sucção')
        cylinder(f,(.4,0,1),.25,1.4,axis='z',color=c('Selo mecânico'),label='Descarga')
        cuboid(f,0,-.8,0,3.2,1.6,.2,steel,'Base')
    elif machine=='Esteira transportadora':
        cuboid(f,0,-.85,1,7,1.7,.18,c('Correia'),'Correia')
        for x in (.5,2,3.5,5,6.5): cylinder(f,(x,0,.7),.26,.45,color=c('Roletes'),label='Rolete')
        cuboid(f,0,-.8,0,.2,.2,1,steel,'Estrutura');cuboid(f,6.8,.6,0,.2,.2,1,steel,'Estrutura')
        cylinder(f,(-1,0,.8),.45,.9,color=c('Motor'),label='Motor')
    else:
        cylinder(f,(0,0,1),.62,2.5,color=c('Reservatório'),label='Reservatório')
        cylinder(f,(1,0,1.9),.38,1.4,color=c('Cabeçote'),label='Cabeçote')
        cuboid(f,-.2,-.6,0,2.8,1.2,.3,steel,'Base')
        cylinder(f,(-.9,0,.9),.4,.7,color=c('Motor'),label='Motor')
    f.update_layout(template='plotly_dark',height=460,margin=dict(l=0,r=0,t=0,b=0),showlegend=False,scene=dict(bgcolor='#0b1424',aspectmode='data',xaxis=dict(visible=False),yaxis=dict(visible=False),zaxis=dict(visible=False)),paper_bgcolor='#0b1424')
    return f
