#!/bin/bash

WORLD_PATH=""
SNAPSHOT_DIR=""
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $SNAPSHOT_DIR

# Para o servidor
cd /home
sudo docker compose stop

# Compacta
tar -czf $SNAPSHOT_DIR/snapshot_$TIMESTAMP.tar.gz -C $(dirname $WORLD_PATH) $(basename $WORLD_PATH)

# Sobe o servidor
sudo docker compose start

echo "Snapshot criado: snapshot_$TIMESTAMP.tar.gz"