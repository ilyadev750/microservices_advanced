docker run -d \
  --name nginx \
  --volume ./nginx.conf:/etc/nginx/nginx.conf \
  --network=custom_network \
  --rm -p 80:80 \
  nginx