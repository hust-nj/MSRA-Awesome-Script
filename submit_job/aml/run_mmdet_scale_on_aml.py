import argparse
import os
import time
import shutil
import glob

print('env:')
print(os.environ)
os.system("ls")
parser = argparse.ArgumentParser(description='Helper run')
# general
parser.add_argument('--data', help='data input', type=str, default='.')
parser.add_argument('--auth', help='auth', required=True, type=str)
parser.add_argument('--path', help='path', required=True, type=str)
parser.add_argument(
    '--cfg', help='experiment configure file name', required=True, type=str)
parser.add_argument(
    '--launcher',
    choices=['none', 'pytorch', 'slurm', 'mpi', 'infimpi'],
    default='pytorch',
    help='job launcher')
parser.add_argument(
    '--branch', help="branch of code", type=str, default='master')
# parser.add_argument(
# '--remove', help="remove the code", action='store_false')

args, rest = parser.parse_known_args()
print('data: {}'.format(args.data))
print('path: {}'.format(args.path))
print('cfg: {}'.format(args.cfg))
print('branch: {}'.format(args.branch))
extra_args = ' '.join(rest)
print('extra_args: {}'.format(extra_args))

folders = glob.glob('{}/jobs/*/{}'.format(os.environ['HOME'], os.environ['DLWS_JOB_ID']))
assert len(folders) == 1
jobdir = folders[0]
print('jobdir: {}'.format(jobdir))
clone_dir = os.path.join(jobdir, 'mmdet')


os.system("git clone --recursive https://{0}@github.com/hust-nj/mmdetection -b {1} {2}".format(args.auth, args.branch, clone_dir))
os.chdir(os.path.join(clone_dir))
os.system('pip install mmcv-full')
os.system('pip install -v -e .')
# os.system('ls $HOME')

os.system("ls")
import torch
gpu_count = torch.cuda.device_count()
os.system("python -m torch.distributed.launch --nproc_per_node={0} {1} {2} --launcher {3} {4}".format(gpu_count, args.path, args.cfg, "pytorch", extra_args))