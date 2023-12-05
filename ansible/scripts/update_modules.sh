#!/bin/sh

cd /home/ubuntu
rm -rf sylcon-oddo
git clone -b production git@github.com:ajnaikka/sylcon-oddo.git

sudo rm -fR /odoo/custom/addons/*
sudo mv ~/sylcon-oddo/addons/* /odoo/custom/addons/

#sudo pip install -r /odoo/custom/addons/requirements.txt
#sudo service odoo-server restart 