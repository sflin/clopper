#! /bin/bash
# Start up script to configure cloud instances
export LC_ALL=C
# work-around needed for EC2-instances
if [ -f /sys/hypervisor/uuid ] && [ `head -c 3 /sys/hypervisor/uuid` == ec2 ]; then
    sudo rm /boot/grub/menu.lst
    sudo update-grub-legacy-ec2 -y
    sudo apt-get dist-upgrade -qq --force-yes
fi

sudo apt-get update && sudo apt-get -y upgrade
sudo apt-get -y install python-pip

#install java JDK and set environment variable
sudo apt-get -y install openjdk-8-jdk

# set environment variable!
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
sudo cat >> ~/.bashrc << EOF

export PATH=$JAVA_HOME:$PATH
export JAVA_HOME=$JAVA_HOME
EOF
source ~/.bashrc

# install gcloud API
sudo pip install --upgrade google-cloud-storage

# install packages (git, maven, gradle)
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
sudo ldconfig
python -c 'import pygit2'
sudo pip install untangle

# install grpcio-tools
sudo python -m pip install grpcio
sudo python -m pip install grpcio-tools

cd ~
mkdir tmp

# get hopper
git clone https://github.com/sealuzh/hopper.git
