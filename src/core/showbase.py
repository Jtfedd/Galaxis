# This file is a workaround for initializing showbase
# and its global variables in such a way that PyCharm
# recognizes it and doesn't throw errors everywhere

# Import ShowBase
from direct.showbase.ShowBase import ShowBase

# Initialize ShowBase
base = ShowBase()

# Provide references for common variables
render = base.render
aspect2d = base.aspect2d
render2d = base.render2d
loader = base.loader
taskMgr = base.taskMgr
messenger = base.messenger
globalClock = globalClock