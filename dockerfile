FROM python:3.12

RUN apt-get update \
    && apt-get install -y

ARG ROOT=/var/www/app

RUN mkdir -p ${ROOT}
ADD . ${ROOT}
WORKDIR ${ROOT}

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "gunicorn", "config.wsgi:application", \
    "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "4"]


