FROM alpine:latest

RUN apk update && \
    apk add --no-cache openssl curl bash

WORKDIR /app

RUN curl -o 111.sh https://raw.githubusercontent.com/eooce/test/main/111.sh

RUN chmod +x 111.sh

CMD ["./111.sh"]
