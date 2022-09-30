#!/bin/bash

if [ ! $1 ]; then
  echo "./${0} <rigname>"
  exit 1
fi

sudo apt-get remove -y docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

if [ ! "$(dpkg -l docker-ce)" ]; then
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    sudo docker stop -t 0 watchtower
    sudo docker stop -t 0 prometheus
    sudo docker rm watchtower
    sudo docker rm prometheus
fi

if [ "$(docker ps -q -f name=watchtower)" ]; then
    sudo docker stop -t 0 watchtower
    sudo docker rm watchtower
fi

sudo docker create \
    --name watchtower \
    --restart always \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    -v /etc/localtime:/etc/localtime:ro \
    containrrr/watchtower \
    --cleanup \
    --interval 3600
sudo docker start watchtower

if [ $2 ]; then
    sudo docker stop -t 0 prometheus
    sudo docker rm prometheus
fi

if [ ! "$(docker ps -q -f name=prometheus)" ]; then
    sudo docker create \
        --name prometheus \
        --network host \
        --restart always \
        -v /run/hive:/run/hive \
        -e MODE=push \
        -e PUSHSERVER="tomcsi.synology.me:9091" \
        -e RIG_NAME=$1 \
        ghcr.io/tomcsi/hiveos-prometheus:main
    sudo docker start prometheus
fi

