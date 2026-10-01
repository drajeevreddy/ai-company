#!/bin/bash
# LocalAI (CPU image generation) helper — Docker lifecycle + image gen.
# Usage: ./manage.sh start|stop|restart|status|logs|image [prompt] [size]
# Adjust LOCALAI_DIR / PORT / CONTAINER to taste.

CONTAINER=local-ai
PORT=8080
LOCALAI_DIR="$HOME/.localai"

start() {
  if sudo docker ps -a --format '{{.Names}}' | grep -q "^$CONTAINER$"; then
    sudo docker start "$CONTAINER"
  else
    sudo docker run -d --name local-ai \
      -p $PORT:$PORT \
      -v $LOCALAI_DIR/models:/models \
      -v $LOCALAI_DIR/backends:/backends \
      -v $LOCALAI_DIR/data:/data \
      -v $LOCALAI_DIR/configuration:/configuration \
      localai/localai:latest
    # Fedora/SELinux: relabel bind mounts so the container can read them
    sudo chcon -Rt svirt_sandbox_file_t $LOCALAI_DIR 2>/dev/null
    sudo docker restart $CONTAINER
  fi
  echo "Waiting for LocalAI..." && sleep 10
  curl -s http://localhost:$PORT/v1/models
}

stop()   { sudo docker stop $CONTAINER; }
status() { sudo docker ps --filter name=$CONTAINER --format '{{.Status}}'; }
logs()   { sudo docker logs --tail 50 $CONTAINER; }

image() {
  PROMPT="${1:-a cute baby sea otter}"
  SIZE="${2:-512x512}"
  curl -s http://localhost:$PORT/v1/images/generations \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$PROMPT\", \"size\": \"$SIZE\"}" | python3 -c 'import sys,json; print(json.load(sys.stdin)["data"][0]["url"])'
}

case "${1:-status}" in
  start) start ;;
  stop)  stop ;;
  restart) stop; sleep 2; start ;;
  status) status ;;
  logs)  logs ;;
  image) image "$2" "$3" ;;
  *) echo "Usage: $0 start|stop|restart|status|logs|image [prompt] [size]" ;;
esac