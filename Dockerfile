FROM python:3.8.5
ENV PYTHONUNBUFFERED 1


RUN apt-get update && apt-get install -y python-pip python-dev libpq-dev gettext

# Install python requirements
ADD requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN apt-get install -y uvicorn


WORKDIR /alakine

# Add files
ADD ./ /alakine/
ADD ./.env_template /alakine/.env


ENV APPLICATION_TO_RUN="uvicorn main_web:app --host 0.0.0.0 --port 80"

EXPOSE 80
# CMD [ "uvicorn", "web_main:app", "--host", "0.0.0.0", "--port", "80" ]
CMD $APPLICATION_TO_RUN
