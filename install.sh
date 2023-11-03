#!/bin/bash

## Create Folders
mkdir -p /etc/fan-manager/conf.d/
mkdir -p /etc/fan-manager/bin
mkdir -p /var/log/fan-manager

## Copy in new files
cp ./conf.d/* /etc/fan-manager/conf.d/
cp ./fan-manager.py /etc/fan-manager/bin/
cp ./Logger.py /etc/fan-manager/bin/
cp ./fan-manager.service /etc/systemd/system/

# Ensure Permissions
chmod 774 /etc/fan-manager/bin/fan-manager.py

## Create link in bin
ln -s /etc/fan-manager/bin/fan-manager.py /usr/bin/fan-manager

## Enable Service
systemctl enable /etc/systemd/system/fan-manager.service
