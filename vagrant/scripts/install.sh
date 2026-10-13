#!/bin/sh
sudo useradd -G vagrant oracle
sudo dnf update
sudo dnf install -y zip unzip net-tools curl wget python3.9 policycoreutils-python-utils bc
