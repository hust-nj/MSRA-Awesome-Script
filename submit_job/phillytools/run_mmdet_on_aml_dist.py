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
print('pwd: {}'.format(os.getcwd()))
print('env:')
print(os.environ)
print("ls")
os.system("ls")
parser = argparse.ArgumentParser(description='Helper run')
# general
parser.add_argument(
    '--cfg', help='experiment configure file name', required=True, type=str)
parser.add_argument(
    '--launcher',
    choices=['none', 'pytorch', 'slurm', 'mpi', 'infimpi'],
    default='mpi',
    help='job launcher')
parser.add_argument(
    '--branch', help="branch of code", type=str, default='master')

args, rest = parser.parse_known_args()
print('cfg: {}'.format(args.cfg))
print('branch: {}'.format(args.branch))
extra_args = ' '.join(rest)
print('extra_args: {}'.format(extra_args))

is_master = ompi_rank() == 0 or ompi_size() == 1
clone_dir = os.path.join(os.getcwd(), 'mmdet')
done_signal_path = os.path.join(os.getcwd(), 'done.txt')

master_init_done = os.path.exists(clone_dir) and os.path.exists(done_signal_path)
if not is_master:
    time.sleep(30.0)
    master_init_done = False
    while not master_init_done:
        print('rank {} waiting for git clone'.format(ompi_rank()))
        master_init_done = os.path.exists(clone_dir) and os.path.exists(done_signal_path)
        time.sleep(10.0)
    os.chdir(clone_dir)
elif master_init_done:
    print('mmdetection master already fully inited')
else:
    os.system("git clone https://github.com/hust-nj/mmdetection -b dist-bug --depth=1 {}".format(clone_dir))
    # only master need to install package
    os.chdir(clone_dir)
    os.system('pip install -v -e .')
    os.system('echo done > {}'.format(done_signal_path))

if is_master:
    os.system("ls")


os.system("python tools/train.py {0} --launcher {1} {2}".format(args.cfg, args.launcher, extra_args))