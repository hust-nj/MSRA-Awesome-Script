import json
import requests
from requests_ntlm import HttpNtlmAuth
import copy
import argparse
import os
from tempfile import NamedTemporaryFile
import pprint
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from getpass import getuser, getpass
import glob


alias = getuser()
def parse_args():
    parser = argparse.ArgumentParser(description='hack philly vc')
    parser.add_argument('--name', type=str, help='Job Name', default='gnn')
    parser.add_argument('--user', type=str, help='hack user name', default=f'{alias}')
    parser.add_argument('--password', type=str, help='hack user password')
    parser.add_argument('--VcId', type=str, help='VcId', default='nextmsra')
    parser.add_argument('--ClusterId', type=str, help='ClusterId', default='eu1')
    parser.add_argument('--gpus', type=int, help='Gpu numbers', default=1)
    parser.add_argument('--path', type=str, help='python scrip path', default='tools/train.py')
    parser.add_argument('--branch', type=str, help='git branch to pull', default='master')
    parser.add_argument('--isdebug', type=bool, help='set to use debug mod', default=False)
    parser.add_argument('--writeDir', type=str, help='the directory to store the result', default='/blob/v-jining/result/gnn/')

    return parser.parse_known_args()


args, rest = parse_args()
extra_args = ' '.join(rest)

if args.password is None:
    passwd = getpass('Password: ')
else:
    passwd = args.password
pwd = {f'{alias}': f'{passwd}'}

submitted_jobId = []
cfgs = ['configs/faster_rcnn/faster_rcnn_r50_fpn_2x_coco.py']
pprint.pprint(cfgs)

gpus8_clusters = ['sc3', 'philly-prod-cy4']

submit_url = 'https://philly/api/v2/submit'
submit_headers = {'Content-Type': 'application/json'}

ClusterId = args.ClusterId
VcId = args.VcId
path = args.path
user = args.user
branch = args.branch
auth = 'input your key'
gpus = args.gpus
writeDir = args.writeDir
philly_auth = HttpNtlmAuth(user, pwd[user])

submit_data = {}

if ClusterId in ['eu1', 'eu2']:
    submit_data = {
        "volumes": {
                "eastusblob1_data": {
                    "type": "blobfuseVolume",
                    "storageAccount": "eastusblob1",
                    "containerName": "data",
                    "path": "/blob/data"
                },
                "myblob": {
                    "type": "blobfuseVolume",
                    "storageAccount": "jianing",
                    "containerName": "v-jining",
                    "path": "/blob/v-jining"
                }
            },
        "credentials": {
            "storageAccounts": {
                "eastusblob1": {
                    "key": "input your key"
                },
                "jianing": {
                    "key": "input your key"
                }
            }
        }
    }

if ClusterId in ['rr1', 'rr2', 'rr3']:
    submit_data = {
        "volumes": {
                "myblob": {
                    "type": "blobfuseVolume",
                    "storageAccount": "njrr1",
                    "containerName": "v-jining",
                    "path": "/blob/v-jining"
                }
            },
        "credentials": {
            "storageAccounts": {
                "njrr1": {
                    "key": "input your key"
                }
            }
        }
    }


############## For blob purpose #######################


if writeDir is None:
    writeDir = '/blob/result/gnn/'
# submit_data["OutputRoot"] = {
#     "Path": "/blob/output",
#     "Name": "outputDir"
# }
submit_data["ClusterId"] = ClusterId
submit_data["VcId"] = VcId
submit_data["UserName"] = user
submit_data["BuildId"] = 0
submit_data["ToolType"] = None
submit_data["Inputs"] = [
    {
        "Name": "dataDir",
        "Path": "/blob/v-jining/data/"
    },
]
submit_data["Outputs"] =[]
submit_data["IsDebug"] = args.isdebug
submit_data["RackId"] = "anyConnected"
submit_data["MinGPUs"] = gpus
submit_data["PrevModelPath"] = None
submit_data["ExtraParams"] = "--cfg {0} --path {1} --branch {2} --auth {3} --writeDir {4} {5}"
submit_data["SubmitCode"] = "p"
submit_data["IsMemCheck"] = False
submit_data["IsCrossRack"] = False
submit_data["Registry"] = "docker.io"
submit_data["Repository"] = "ninja0/mmdet"
submit_data["Tag"] = "latest"
submit_data["OneProcessPerContainer"] = False
submit_data["NumOfContainers"] = str(gpus//8) if ClusterId in gpus8_clusters else str(gpus//4)
submit_data["dynamicContainerSize"] = False
if VcId in ['eu1', 'eu2']:
    submit_data["Queue"] = "bonus"
for cfg in cfgs:

    data = submit_data.copy()
    data["ConfigFile"] = "/blob/v-jining/configfile/run_gnn_on_philly.py"
    data["JobName"] = os.path.splitext(os.path.basename(cfg))[0] + '_' + args.name
    # if ClusterId in ['gcr', 'rr1', 'rr2', 'cam', 'philly-prod-cy4']:
    #     data["CustomMPIArgs"] = "env CUDA_CACHE_DISABLE=1 NCCL_SOCKET_IFNAME=ib0 NCCL_DEBUG=INFO OMP_NUM_THREADS=2"
    # else:
    #     data["CustomMPIArgs"] = "env CUDA_CACHE_DISABLE=1 NCCL_IB_DISABLE=1 NCCL_SOCKET_IFNAME=eth0 NCCL_DEBUG=INFO OMP_NUM_THREADS=2"

    data['ExtraParams'] = data['ExtraParams'].format(cfg, path, branch, auth, writeDir, extra_args)

    r = requests.post(json=data, url=submit_url, auth=philly_auth, headers=submit_headers, verify=False)
    if r.status_code == 200:
        res = r.json()
        print("submit {0} to {1} successfully".format(data['JobName'], ClusterId))
        print(res)
        res_dict = {}
        res_dict["JobName"] = data["JobName"]
        res_dict["AppId"] = res['jobId']
        res_dict["cfg"] = cfg
        res_dict["Link"] = "https://philly/#/job/{}/{}/{}".format(ClusterId, VcId, res['jobId'][12:])
        submitted_jobId.append(res_dict)
    else:
        print(r)
        print('submit failed with status_code {}'.format(r.status_code))

pprint.pprint(submitted_jobId)
