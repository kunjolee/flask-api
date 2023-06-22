FROM python:3.11
EXPOSE 5000
WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# from your filesystem into container file system = current into /app/
COPY . .

CMD ["flask", "--app", "main:create_app", "run", "--host", "0.0.0.0" ]