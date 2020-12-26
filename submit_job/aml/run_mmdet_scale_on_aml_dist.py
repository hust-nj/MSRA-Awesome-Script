import argparse
import os
import time
import shutil


def ompi_rank():
    """Find OMPI world rank without calling mpi functions
    :rtype: int
    """
    return int(os.environ.get('OMPI_COMM_WORLD_LOCAL_RANK') or 0)


def ompi_size():
    """Find OMPI world size without calling mpi functions
    :rtype: int
    """
    return int(os.environ.get('OMPI_COMM_WORLD_SIZE') or 1)


print('rank: {}'.format(ompi_rank()))
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
    default='mpi',
    help='job launcher')
parser.add_argument(
    '--branch', help="branch of code", type=str, default='master')
parser.add_argument(
'--remove', help="remove the code", action='store_false')

args, rest = parser.parse_known_args()
print('data: {}'.format(args.data))
print('path: {}'.format(args.path))
print('cfg: {}'.format(args.cfg))
print('branch: {}'.format(args.branch))
extra_args = ' '.join(rest)
print('extra_args: {}'.format(extra_args))

is_master = ompi_rank() == 0 or ompi_size() == 1
clone_dir = os.path.join(os.environ['HOME'], 'mmdet')
done_signal_path = os.path.join(os.environ['HOME'], 'done.txt')

if args.remove:
    if is_master and os.path.exists(done_signal_path):
        print("Removing the signal...")
        os.remove(done_signal_path)

master_init_done = os.path.exists(clone_dir) and os.path.exists(done_signal_path)
if not is_master:
    time.sleep(30.0)
    master_init_done = False
    while not master_init_done:
        print('rank {} waiting for git clone'.format(ompi_rank()))
        master_init_done = os.path.exists(clone_dir) and os.path.exists(done_signal_path)
        time.sleep(10.0)
elif master_init_done:
    # os.remove(done_signal_path)
    # os.chdir(os.path.expanduser('~/mmdet'))
    # os.system('pip install --user future tensorboard')
    # os.system('sh ./compile.sh')
    # os.system('pip install --user -e .')
    # os.system('echo done > $HOME/done.txt')
    print('mmdetection master already fully inited')
else:
    if os.path.exists(os.path.join(os.environ['HOME'], 'mmdet')):
        print("deleting...")
        shutil.rmtree(os.path.expanduser(os.path.join(os.environ['HOME'], 'mmdet')))
    os.system("git clone --recursive https://{0}@github.com/zdaxie/mmdet_scale -b {1} $HOME/mmdet".format(args.auth, args.branch))
    # only master need to install package
    os.chdir(os.path.join(os.environ['HOME'], 'mmdet'))
    # os.system('pip install mmcv-full')
    os.system('pip install --user -e .')
    os.system('echo done > $HOME/done.txt')
    os.system('ls $HOME')

os.chdir(os.path.join(os.environ['HOME'], 'mmdet'))
if is_master:
    os.system("ls")

print("python {0} {1} --launcher {2} {3}".format(args.path, args.cfg, 'mpi', extra_args))
os.system("NCCL_TREE_THRESHOLD=0 NCCL_SOCKET_IFNAME=eth0 python {0} {1} --launcher {2} {3}".format(args.path, args.cfg, args.launcher, extra_args))