# https://nabajyotiborah.medium.com/fastapi-scalable-project-structure-with-docker-compose-45dc3a9fb4c6
FROM python:3.10

# 
WORKDIR /code

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

# 
#CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
EXPOSE 80
