docker run -d \
  --name nginx \
  --volume ./nginx.conf:/etc/nginx/nginx.conf \
  --volume /etc/letsencrypt:/etc/letsencrypt:ro \
  --network=microservices_advanced_custom_network \
  -p 80:80 \
  -p 443:443 \
  nginx