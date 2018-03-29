FROM python:3.5-jessie

WORKDIR /app
ENV FLASK_APP controller.py
RUN mkdir /etc/configs && chmod +r -R /etc/configs
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . /app

ENTRYPOINT [ "python", "start.py"]
