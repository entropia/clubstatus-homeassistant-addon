FROM python:3.14.0-slim
ENV PYTHONUNBUFFERED=1

MAINTAINER henry@entropia.de
COPY app/requirements.txt ./
RUN pip install -r requirements.txt
RUN mkdir /app
COPY app/spaceapi.py /app/spaceapi.py
RUN chmod u+x /app/spaceapi.py

WORKDIR /app
CMD ["flask", "--app", "spaceapi", "run", "-h", "0.0.0.0", "--with-threads"]
