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

# get hopper
git clone https://github.com/sealuzh/hopper.git
echo hello

# get clopper
#git clone https://github.com/
#start server aka cloud-manager
# python server.py
#(server sends "hello" from instances)
