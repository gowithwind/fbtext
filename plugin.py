plugins={}
def register(key,func):
      plugins[key]=func
def z(ui):
	ui.info='a plugin from z'

register('z',z)