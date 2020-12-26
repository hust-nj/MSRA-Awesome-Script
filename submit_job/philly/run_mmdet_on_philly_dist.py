import argparse
import os
import time
from torch.utils.model_zoo import load_url
from mmcv import Config

model_urls = {
    'resnet50': 'https://download.pytorch.org/models/resnet50-19c8e357.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-b121ed2d.pth',
}

open_mmlab_model_urls = {
    'vgg16_caffe': 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/pretrain/third_party/vgg16_caffe-292e1171.pth',  # noqa: E501
    'resnet50_caffe': 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/pretrain/third_party/resnet50_caffe-788b5fa3.pth',  # noqa: E501
    'resnet101_caffe': 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/pretrain/third_party/resnet101_caffe-3ad79236.pth',  # noqa: E501
    'resnext101_32x4d': 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/pretrain/third_party/resnext101_32x4d-a5af3160.pth',  # noqa: E501
    'resnext101_64x4d': 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/pretrain/third_party/resnext101_64x4d-ee2c6f71.pth',  # noqa: E501
    'contrib/resnet50_gn': 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/pretrain/third_party/resnet50_gn_thangvubk-ad1730dd.pth',  # noqa: E501
    'detectron/resnet50_gn': 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/pretrain/third_party/resnet50_gn-9186a21c.pth',  # noqa: E501
    'detectron/resnet101_gn': 'https://s3.ap-northeast-2.amazonaws.com/open-mmlab/pretrain/third_party/resnet101_gn-cac0ab98.pth'  # noqa: E501
}  # yapf: disable


def prepare_pretrain_model(filename):
    if filename.startswith('modelzoo://'):
        model_name = filename[11:]
        load_url(model_urls[model_name], progress=False)
    elif filename.startswith('open-mmlab://'):
        model_name = filename[13:]
        load_url(open_mmlab_model_urls[model_name], progress=False)
    elif filename.startswith(('http://', 'https://')):
        load_url(filename, progress=False)
    else:
        if not os.path.isfile(filename):
            raise IOError('{} is not a checkpoint file'.format(filename))


def ompi_rank():
    """Find OMPI world rank without calling mpi functions
    :rtype: int
    """
    return int(os.environ.get('OMPI_COMM_WORLD_RANK') or 0)


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
    '--branch', help="branch of code", type=str, default='master')
args, rest = parser.parse_known_args()
print(args)
extra_args = ' '.join(rest)
print('extra_args: {}'.format(extra_args))

is_master = ompi_rank() == 0 or ompi_size() == 1
clone_dir = os.path.join(os.environ['HOME'], 'mmdetection')
done_signal_path = os.path.join(os.environ['HOME'], 'done.txt')
master_init_done = os.path.exists(clone_dir) and os.path.exists(
    done_signal_path)
torch_model_zoo_path = '/hdfs/public/v-yuca/torch_model_zoo'
os.environ['TORCH_MODEL_ZOO'] = torch_model_zoo_path
if not is_master:
    while not master_init_done:
        print('rank {} waiting for git clone'.format(ompi_rank()))
        master_init_done = os.path.exists(clone_dir) and os.path.exists(
            done_signal_path)
        time.sleep(10.0)
elif master_init_done:
    print('mmdetection master already fully inited')
else:
    os.system(
        "git clone --recursive https://{0}@github.com/hust-nj/VC_DET_PRV -b {1} $HOME/mmdetection"
        .format(args.auth, args.branch))
    # only master need to install package
    os.system("sudo apt-get install cuda-compat-10.2")
    os.system("export LD_LIBRARY_PATH=/usr/local/cuda-10.2/compat:$LD_LIBRARY_PATH")
    os.chdir(os.path.expanduser('~/mmdetection'))
    os.system('./init_philly.sh')
    cfg = Config.fromfile(args.cfg)
    pretrained = cfg.get("pretrained", None)
    if pretrained is not None:
        try:
            prepare_pretrain_model(pretrained)
        except OSError:
            print('OSError Error. Unset TORCH_MODEL_ZOO')
            del os.environ['TORCH_MODEL_ZOO']
            prepare_pretrain_model(pretrained)
    os.system('echo done > $HOME/done.txt')
    os.system('ls $HOME')
os.chdir(os.path.expanduser('~/mmdetection'))
if is_master:
    os.system("ls")
os.system("python {0} {1} --launcher {2} {3}".format(args.path, args.cfg,
                                                     'mpi', extra_args))
