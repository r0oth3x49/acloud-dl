FROM python:3.9-slim

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "/opt/app/acloud-dl.py"]
