FROM alpine:latest
RUN apk add --no-cache sqlite xray curl bash jq
WORKDIR /app
COPY config.json /etc/xray/config.json
COPY entrypoint.sh /entrypoint.sh
COPY server.py /app/server.py
COPY log-user.sh /usr/local/bin/log-user.sh
RUN chmod +x /entrypoint.sh /usr/local/bin/log-user.sh
EXPOSE 8080 8081
CMD ["/entrypoint.sh"]