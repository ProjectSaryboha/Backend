FROM python:3.11.9

WORKDIR /Backend
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "-u", "app.py"]