FROM python:3.12-rc-alpine

RUN apk --no-cache add --virtual .builddeps gcc gfortran musl-dev     && pip install numpy==1.26.0     && apk del .builddeps     && rm -rf /root/.cache
