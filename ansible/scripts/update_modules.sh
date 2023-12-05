#!/bin/sh

cd /home/ubuntu
rm -rf sylcon-odoo
git clone -b production git@github.com:ajnaikka/sylcon-oddo.git

sudo rm -fR /odoo/custom/addons/*
sudo mv ~/sylcon-odoo/addons/* /odoo/custom/addons/

sudo pip install -r /odoo/custom/addons/requirements.txt
sudo service odoo-server restart 