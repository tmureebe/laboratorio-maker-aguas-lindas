"""Leitura/exportação STL e transformações sem bibliotecas CAD."""
import numpy as np
import struct
from pathlib import Path

def read(path):
    raw=Path(path).read_bytes()
    dtype=np.dtype([('normal','<f4',3),('v','<f4',(3,3)),('attr','<u2')])
    if len(raw)>84 and len(raw)==84+50*struct.unpack_from('<I',raw,80)[0]:
        return np.frombuffer(raw,dtype=dtype,offset=84)['v'].astype(float)
    return np.array([list(map(float,line.split()[1:])) for line in raw.decode().splitlines()
                     if line.strip().startswith('vertex ')]).reshape(-1,3,3)

def write(path,tris):
    tris=np.asarray(tris);n=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0])
    n/=np.maximum(np.linalg.norm(n,axis=1),1e-12)[:,None]
    data=np.zeros(len(tris),dtype=np.dtype([('normal','<f4',3),('v','<f4',(3,3)),('attr','<u2')]))
    data['normal']=n;data['v']=tris
    Path(path).write_bytes(b'V7 MODELO DIGITAL EM MM'.ljust(80,b' ')+struct.pack('<I',len(data))+data.tobytes())

def rotation(axis,angle):
    theta=np.deg2rad(angle);c=np.cos(theta);s=np.sin(theta)
    return dict(x=np.array([[1,0,0],[0,c,-s],[0,s,c]]),
                y=np.array([[c,0,s],[0,1,0],[-s,0,c]]),
                z=np.array([[c,-s,0],[s,c,0],[0,0,1]]))[axis]

def transform(tris,matrix=None,xyz=(0,0,0)):
    return np.asarray(tris)@(np.eye(3) if matrix is None else matrix).T+np.array(xyz)
