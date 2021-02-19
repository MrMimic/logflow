FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04

RUN apt-get update && DEBIAN_FRONTEND="noninteractive" apt-get install -y --no-install-recommends \
         build-essential \
         cmake \
         git \
         curl \
         ca-certificates \
         libjpeg-dev \
         libpng-dev \
	 python3.6 \
	 python3.6-dev \
	 python3-distutils \
	 nano \
	 htop \
         python3-sphinx \
	 iotop && \
     rm -rf /var/lib/apt/lists/*

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.6 get-pip.py
RUN pip install numpy cython typing loguru h5py tqdm word2vec mypy sphinx coverage sphinx-rtd-theme pandas
RUN pip install fastapi uvicorn
RUN pip install torch torchvision twine #Only for cuda 10.2


