FROM python:3.7-slim

WORKDIR /foodgram-project-react

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python3", "manage.py", "migrate"]
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]