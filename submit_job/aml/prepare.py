#
# This Python script prepares the environments before running the specific job.
#
# Author: Philly Beijing Team <PhillyBJ@microsoft.com>
#
# Specifically, we do following things here:
#     1. Create a new workspace with a specified name, if it does not exist, connect to it and write its config to a local file.
#     2. Create a compute with a specified name in the workspace for training jobs to run on.
#     3. Register an existing datastore to the workspace.
#

import os
import sys

import azureml.core
from azureml.core import Workspace
from azureml.core import Datastore
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException

from azureml.contrib.core.compute import AksCompute

# from configs.base_config import config

from mmcv import Config
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--cfg', default='configs/base_config.py')
args, _ = parser.parse_known_args()

config = Config.fromfile(args.cfg).config

#
# Configurations
#
subscription_id = config.subscription_id
resource_group = config.resource_group
workspace_name = config.workspace_name
cluster_name = config.cluster_name
datastore_name = config.datastore_name
blob_container_name = config.data_blob.blob_container_name
blob_account_name = config.data_blob.blob_account_name
blob_account_key = config.data_blob.blob_account_key

#
# Prepare the workspace.
#
ws = None
try:
    print("Connecting to workspace '%s'..." % workspace_name)
    ws = Workspace(subscription_id=subscription_id, resource_group=resource_group, workspace_name=workspace_name)
except:
    print("Workspace not accessible.")
print(ws.get_details())

ws.write_config()

#
# Prepare the compute in the workspace.
#
try:
    # ct = ComputeTarget(workspace=ws, name=cluster_name)
    ct = AksCompute(workspace=ws, name=cluster_name)
    print(ct)
    print("Found existing cluster '%s'. Skip." % cluster_name)
except ComputeTargetException:
    print("ComputeTarget not accessible.")
# print(ct.get_status().serialize())

#
# Register an existing datastore to the workspace.
#
if datastore_name not in ws.datastores:
    Datastore.register_azure_blob_container(
        workspace=ws,
        datastore_name=datastore_name,
        container_name=blob_container_name,
        account_name=blob_account_name,
        account_key=blob_account_key
    )
    print("Datastore '%s' registered." % datastore_name)
else:
    print("Datastore '%s' has already been regsitered." % datastore_name)

# (END)
