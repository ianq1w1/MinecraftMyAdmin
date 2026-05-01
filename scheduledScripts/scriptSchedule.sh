WORLD_PATH="/vps/volumedocker/worlds/path"
SNAPSHOT_DIR="/vps/compressed_snapshots-path/"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $SNAPSHOT_DIR

cd /docker-compose/path

sudo docker compose stop

# Compacta
tar -czf $SNAPSHOT_DIR/snapshot_$TIMESTAMP.tar.gz -C $(dirname $WORLD_PATH) $(basename $WORLD_PATH)

# Sobe o servidor
sudo docker compose start