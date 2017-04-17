# Same as boc10, except that here ndim=40 (i.e. Fig. 5 of paper)
from mods.Lorenz95.boc10 import *

m = 40
f['m'] = m
X0 = GaussRV(m=m, C=0.001)

obsInds = arange(0,m,2)
p       = len(obsInds)
@atmost_2d
def hmod(E,t): return E[:,obsInds]
H = direct_obs_matrix(m,obsInds)
h = {
    'm'    : p,
    'model': hmod,
    'jacob': lambda x,t: H,
    'noise': GaussRV(C=1.5*eye(p)),
    'plot' : lambda y: plt.plot(obsInds,y,'g*',ms=8)[0]
    }
 
other = {'name': os.path.relpath(__file__,'mods/')}

setup = OSSE(f,h,t,X0,**other)

####################
# Suggested tuning
####################
# NB: To  be pretty sure that the particle filter configuration
# is robust against divergence, must test at least up to T=2000.
#                                                                   # rmse_a 
#cfgs.add(EnKF,'Sqrt',N=24,rot=True,infl=1.05)
#cfgs.add(EnKF_N,N=24,rot=True,infl=1.01)
#cfgs.add(PFD,     N=100, xN=1000,NER=0.9,reg=0.7,Qs=0.8,nuj=False) # 1.05
#cfgs.add(PFD,     N=1000,xN=100, NER=0.9,reg=0.4,Qs=0.5,nuj=False) # 0.52
#cfgs.add(PartFilt,N=3000,NER=0.20,reg=1.2,nuj=True)                # 0.77
#cfgs.add(PartFilt,N=5000,NER=0.10,reg=1.1,nuj=True)                # 0.72
#cfgs.add(PartFilt,N=10000,NER=0.05,reg=0.8,nuj=True)               # 0.45