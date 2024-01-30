FROM odoo:17.0

USER root

COPY ./addons/requirements.txt /mnt/extra-addons/requirements.txt

RUN set -e; \
    pip3 install --no-cache-dir -r /mnt/extra-addons/requirements.txt

USER odoo


