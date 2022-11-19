FROM python:3.9.5-alpine
WORKDIR /nutritionassistant
ADD . /nutritionassistant

RUN set -e; \
        apk add --no-cache --virtual .build-deps \
                gcc \
                libc-dev \
                linux-headers \
                mariadb-dev \
                python3-dev \
                postgresql-dev \
        ;
COPY requirements.txt /nutritionassistant
RUN pip install -r requirements.txt
CMD ["python","app.py"]
