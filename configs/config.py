from yacs.config import CfgNode as CN

_C = CN()

_C.NETWORK = CN()
_C.NETWORK.ARCH = ""
_C.NETWORK.PARAMS = CN()
_C.NETWORK.PARAMS.state_dim= 4 
_C.NETWORK.PARAMS.action_dim = 2 
_C.NETWORK.PARAMS.hidden_size = 256
_C.NETWORK.PARAMS.gamma = 0.99
_C.NETWORK.PARAMS.optimiser = "Adam"
_C.NETWORK.PARAMS.value_lr = 0.001
_C.NETWORK.PARAMS.policy_lr = 0.0001
_C.NETWORK.PARAMS.load_dir = ""
_C.NETWORK.PARAMS.conv= False 
_C.NETWORK.PARAMS.debug= False 
_C.NETWORK.PARAMS.write= True 
_C.NETWORK.PARAMS.output_dir= ""
_C.NETWORK.PARAMS.test_every = 500
_C.NETWORK.PARAMS.save= True #to save every _C.NETWORK.PARAMS.test_every
_C.NETWORK.PARAMS.test_only = False

_C.ENVIRONMENT = CN()
_C.ENVIRONMENT.NAME = ""

_C.TRAIN = CN()
_C.TRAIN.TRAIN = True
_C.TRAIN.ASYNCH = False
_C.TRAIN.WORKERS = 1
_C.TRAIN.TEST = True
_C.TRAIN.SPECS = CN()
_C.TRAIN.SPECS.max_episodes = 10000
_C.TRAIN.SPECS.num_steps = 50

_C.TEST = CN()
_C.TEST.TEST_ONLY = False
_C.TEST.NUMBER = 10
