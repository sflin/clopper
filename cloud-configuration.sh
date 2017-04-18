#! /bin/bash
"""Start up script to configure cloud instances"""
sudo apt-get -y update && sudo apt-get -y upgrade
export LC_ALL=C

#install java JDK and set environment variable
sudo apt-get -y install default-jdk

# set environment variable!
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
sudo cat >> ~/.bashrc << EOF

export PATH=$JAVA_HOME:$PATH
export JAVA_HOME=$JAVA_HOME
EOF
source ~/.bashrc

# install packages (git, pip, maven, gradle)
sudo apt-get -y install python-pip
sudo apt-get -y install git
sudo apt-get -y install maven
sudo apt-get -y install gradle
sudo apt-get -y install cmake

# install specific packages required for libgit2
sudo pip install cffi
sudo pip install six

# install libgit2 and pygit2 version 0.25.0
wget https://github.com/libgit2/libgit2/archive/v0.25.0.tar.gz
tar xzf v0.25.0.tar.gz
cd libgit2-0.25.0/
cmake .
make
sudo make install
cd ..
sudo pip install pygit2==0.25.0
sudo pip install untangle

# install grpcio-tools
sudo python -m pip install grpcio
sudo python -m pip install grpcio-tools

cd ~
mkdir output
mkdir tmp

# get hopper
git clone https://github.com/sealuzh/hopper.git

# get clopper
# wget https://raw.githubusercontent.com/sflin/clopper/master/clopper_pb2.py?token=AOunWIehJcNN6rmF9Ekq3Lb10K18ixefks5Y8KFGwA%3D%3D -O clopper_pb2.py
