docker run -d \
  --name nginx \
  --network=custom_network \
  --rm -p 80:80 \
  nginx