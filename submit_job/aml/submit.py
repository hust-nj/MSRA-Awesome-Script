import argparse
from mmcv import Config

import os
import sys
import pprint
from os.path import isfile, join
from os import listdir

import azureml.core
from azureml.core import Workspace
from azureml.core import Datastore
from azureml.core import Experiment
from azureml.core.compute import ComputeTarget
from azureml.core.container_registry import ContainerRegistry
from azureml.train.estimator import Estimator
from azureml.train.estimator import Mpi
from azureml.train.dnn import PyTorch
from azureml.contrib.core.compute import AksCompute
from azureml.core.runconfig import MpiConfiguration


parser = argparse.ArgumentParser()
parser.add_argument('--cfg', default='configs/base_config.py')
args, _ = parser.parse_known_args()

cfg = Config.fromfile(args.cfg).config
if not isinstance(cfg.params.config_files, list):
    cfg.params.config_files = [cfg.params.config_files]

ws = Workspace.from_config()

ct = ComputeTarget(workspace=ws, name=cfg.cluster_name)
ds = Datastore(workspace=ws, name=cfg.datastore_name)

config_files_list = cfg.params.config_files.copy()
cfg.params.pop('config_files')
for config in config_files_list:
    print("Submit entry script: {}".format(config))

    script_params_dict = {}
    for key in cfg.params:
        script_params_dict[f'--{key}'] = cfg.params[key]
    script_params_dict['--workdir'] = ds.path('.').as_mount()
    script_params_dict['--config_file'] = config

    est = PyTorch(
        compute_target=ct,
        use_gpu=True,
        ## ADD MULTI-NODE SUPPORT
        # node_count=cfg.node_count,
        # distributed_training=Mpi(process_count_per_node=cfg.process_count_per_node),
        # distributed_training=MpiConfiguration(),        

        # shm_size="128G",
        use_docker=True,
        custom_docker_image=cfg.custom_docker_image,
        user_managed=True,
        source_directory=cfg.entry_path,
        entry_script=cfg.entry_file,
        script_params=script_params_dict
    )
    from azureml.contrib.core.k8srunconfig import K8sComputeConfiguration
    # itp
    k8sconfig = K8sComputeConfiguration()
    k8s = dict()
    k8s['preemption_allowed'] = False
    k8s['gpu_count'] = cfg.params.num_gpu
    k8s['enable_ssh'] = True
    k8s['ssh_public_key'] = 'input your key'
    k8sconfig.configuration = k8s
    est.run_config.cmk8scompute = k8sconfig
    # Run the job (i.e. estimator) in an experiment.
    run = Experiment(workspace=ws, name=cfg.experiment_name).submit(est)
    pprint.pprint(run)

