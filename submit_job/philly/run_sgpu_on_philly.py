# single gpu script
import argparse
import os

print('env:')
print(os.environ)
os.system("ls")
parser = argparse.ArgumentParser(description='Helper run')
# general
parser.add_argument('--auth', help='auth', required=True, type=str)
parser.add_argument('--path', help='path', required=True, type=str)
parser.add_argument('--cfg', help='experiment configure file name', required=True, type=str)
parser.add_argument('--branch', help="branch of code", type=str, default='master')
args, rest = parser.parse_known_args()
# print('args: {}'.format(args))
extra_args = ' '.join(rest)
print('extra_args: {}'.format(extra_args))

clone_dir = os.path.join(os.environ['HOME'], adversarial)

os.system("git clone --recursive https://{0}@github.com/sherlockyyc/NLP-Adversarial-Examples -b {1} {2}".format(args.auth, args.branch, clone_dir))
# os.system("pip install tensorboard --user")
os.chdir(clone_dir)
# os.system('bash init_philly.sh')
os.system("python {0} {1} {2}".format(args.path, args.cfg, extra_args))
