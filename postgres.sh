mkdir ~/postgres
cd ~/postgres
mkdir varlib
chmod 777 varlib

touch docker-compose.yml
cat <<EOF > "docker-compose.yml"
version: '3.8'

services:
  db-shared:
    image: postgres:15
    container_name: db-shared
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: postgres
      PGDATA: /var/lib/postgresql/data
    volumes:
      - ./shared_postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    shm_size: 1g
    restart: always
EOF

docker compose up -d