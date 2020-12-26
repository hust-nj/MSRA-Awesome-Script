import os
import argparse
import glob

parser = argparse.ArgumentParser(description="AML Generic Launcher")
parser.add_argument('--auth', default="input-your-auth", help='key for git clone')
parser.add_argument('--branch', default='dev_heatmap')
parser.add_argument('--workdir', default="", help="The working directory.")
parser.add_argument('--launcher', default='mpi')
parser.add_argument('--script_path', default='./tools/train.py')
parser.add_argument('--config_file', default="")
parser.add_argument('--num_gpu', default=8)

args, rest = parser.parse_known_args()
extra_args = ' '.join(rest)
print(args.workdir)
# for itp cluster, compute jobdir first
folders = glob.glob('{}/jobs/*/{}'.format(os.environ['HOME'], os.environ['DLWS_JOB_ID']))
assert len(folders) == 1
jobdir = folders[0]
print('jobdir: {}'.format(jobdir))
clone_dir = os.path.join(jobdir, 'mmdet')


# system_str = f"""
# set -x
# pwd
# env
# nvidia-smi
# git clone --recursive https://{args.auth}@github.com/hust-nj/condconv-reppoints -b {args.branch} {clone_dir}
# cd {clone_dir}
# sudo /opt/miniconda/bin/pip uninstall mmcv-full -y
# sudo /opt/miniconda/bin/pip install -v -e .
# ls
# python -m torch.distributed.launch --nproc_per_node={args.num_gpu} {args.script_path} {args.config_file} --launcher pytorch {extra_args} --aml
# """

system_str = f"""
sleep 10h
"""
os.system(system_str)
