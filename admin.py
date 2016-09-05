from common import *

class Printable:
  def __repr__(self):
    from pprint import pformat
    return "<" + type(self).__name__ + "> " + pformat(vars(self), indent=4, width=1)


class Operator:
  """Class for operators (models)."""
  def __init__(self,m,model=None,noise=None,**kwargs):
    self.m = m

    if model is None:
      model = lambda x,t,dt: x
    self.model = model

    if noise is None:
      noise = 0
    if noise is 0:
      noise = GaussRV(0,m=m)
    self.noise = noise

    # Write the rest of parameters
    for key, value in kwargs.items(): setattr(self, key, value)

class OSSE:
  """Container for OSSE settings."""
  def __init__(self,f,h,t,X0,**kwargs):
    if not isinstance(X0,RV):
      # TODO: Pass through RV instead?
      X0 = GaussRV(**X0)
    if not isinstance(f,Operator):
      f = Operator(**f)
    if not isinstance(h,Operator):
      h = Operator(**h)
    if not isinstance(t,Chronology):
      t = Chronology(**t)
    self.X0 = X0
    self.f  = f
    if h.noise.C.rk != h.noise.C.m:
      raise ValueError("Rank-deficient R not supported")
    self.h  = h
    self.t  = t
    # Write the rest of parameters
    for key, value in kwargs.items(): setattr(self, key, value)

  def __repr__(self):
    s = 'OSSE(' + self.name
    for key,val in self.__dict__.items():
      if key != 'name':
        s += '\n' + key + '=' + str(val)
    return s + ')'

from json import JSONEncoder # TODO: Did this do anything?
class DAM(JSONEncoder):
  """A fancy dict for the settings of DA Method."""
  def __init__(self,da_method,*AMethod,**kwargs):
    self.da_method    = da_method
    if len(AMethod) == 1:
      self.AMethod = AMethod[0]
    # Careful with defaults -- explicit is better than implicit!
    self.liveplotting = False
    # Write the rest of parameters
    for key, value in kwargs.items(): setattr(self, key, value)

  def __repr__(self):
    s = 'DAM(' + self.da_method.__name__
    for key,val in self.__dict__.items():
      if key != 'da_method':
        s += ', ' + key + '=' + str(val)
    return s + ')'

class DAM_list(list,JSONEncoder):
  def add(self,*kargs,**kwargs):
    self.append(DAM(*kargs,**kwargs))

def assimilate(setup,cfg,xx,yy):
  """Call cfg.da_method(), passing along all arguments."""
  args = locals()
  return cfg.da_method(**args)

def simulate(setup):
  """Generate synthetic truth and observations"""
  f,h,chrono,X0 = setup.f, setup.h, setup.t, setup.X0

  # truth
  xx = zeros((chrono.K+1,f.m))
  xx[0] = X0.sample(1)
  # obs
  yy = zeros((chrono.KObs+1,h.m))
  for k,kObs,t,dt in progbar(chrono.forecast_range,'Truth & Obs'):
    xx[k] = f.model(xx[k-1],t-dt,dt) + sqrt(dt)*f.noise.sample(1)
    if kObs is not None:
      yy[kObs] = h.model(xx[k],t) + h.noise.sample(1)
  return xx,yy

class Bunch(dict):
  def __init__(self,**kw):
    dict.__init__(self,kw)
    self.__dict__ = self

# DEPRECATED
import inspect
def dyn_import_all(modpath):
  """Incredibly hackish way to load into caller's global namespace"""
  exec('from ' + modpath + ' import *',inspect.stack()[1][0].f_globals)

# DEPRECATED
# Since it's not possible to
# import module as alias
# from alias import v1 v2 (or *)
def dyn_import_all_2(modpath,namespace):
  """Slightly less_hackish. Call as:
    dyn_import_all_2(modpath,globals())"""
  exec('from ' + modpath + ' import *',namespace)
  # Alternatively
  #modm = importlib.import_module(modpath)
  #namespace.update(modm.__dict__)
  # NB: __dict__ contains a lot of defaults



