# https://nabajyotiborah.medium.com/fastapi-scalable-project-structure-with-docker-compose-45dc3a9fb4c6
FROM python:3.10-slim

# 
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 
COPY ./requirements.txt /app/requirements.txt

#
RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt

# 
COPY ./app /app/app

#
EXPOSE 80
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "80"]

