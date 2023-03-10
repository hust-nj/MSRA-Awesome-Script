FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

# Labels for the docker
LABEL description="This docker has pytorch 2.0 with cuda 11.8, and cudnn 8.0." \
      tag="pytorch2.0-cuda11.8-openmpi" \
      creator="ninja" tooltype="pytorch" \
      tooltypeversion="2.0" \
      createtime="03/01/2023"

USER root:root

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

ENV DEBIAN_FRONTEND=noninteractive

ENV LD_LIBRARY_PATH=/usr/local/cuda/extras/CUPTI/lib64:/usr/local/nvidia/lib:/usr/local/nvidia/lib64

ENV NCCL_DEBUG=INFO

ENV HOROVOD_GPU_ALLREDUCE=NCCL

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmlx4-1 \
    libmlx5-1 \
    librdmacm1 \
    libibverbs1 \
    libmthca1 \
    libdapl2 \
    dapl2-utils openssh-client \
    openssh-server \
    iproute2 && \
    apt-get install -y \
    build-essential \
    bzip2 \
    git \
    tmux \
    wget \
    unzip \
    net-tools \
    libjpeg-dev \
    libpng-dev \
    ca-certificates \
    libopenblas-dev \
    libopencv-dev \
    libyaml-dev \
    ffmpeg libsm6 libxext6 \
    cpio software-properties-common && \
    apt-get update && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/anaconda.sh && \
    sh ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh

ENV PATH=/opt/conda/bin:/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

ENV OPENMPI_VERSION=4.1.5

RUN mkdir /tmp/openmpi && \
    cd /tmp/openmpi && \
    wget https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-${OPENMPI_VERSION}.tar.gz && \
    tar zxf openmpi-${OPENMPI_VERSION}.tar.gz && \
    cd openmpi-${OPENMPI_VERSION} && \
    ./configure --enable-orterun-prefix-by-default && \
    make -j $(nproc) all && \
    make install && \
    ldconfig && \
    rm -rf /tmp/openmpi

RUN export CUDA_HOME="/usr/local/cuda"

RUN pip install terminaltables

RUN pip install future tensorboard

RUN conda config --add channels conda-forge

# install pytorch2.0
# RUN conda install -y cmake ninja mkl mkl-include
# RUN conda install -y -c pytorch magma-cuda118
RUN conda install -y numpy pyyaml scipy ipython mkl scikit-learn matplotlib pandas setuptools Cython h5py graphviz

RUN conda clean -ya

# RUN conda install -y mkl-include cmake cffi typing cython

RUN conda install -y -c mingfeima mkldnn

RUN pip install jinja2

# RUN git clone --recursive https://github.com/pytorch/pytorch -b v2.0.0-rc3 && \
#     cd pytorch && \
#     git submodule sync && \
#     git submodule update --init --recursive && \
#     pip install -r requirements.txt && \
#     export CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"} && \
#     pip install .

RUN add-apt-repository ppa:ubuntu-toolchain-r/test && apt-get update && apt-get upgrade libstdc++6 -y && apt-get clean -y


# replace this line with the torch version you need
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu118


WORKDIR /root