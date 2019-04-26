FROM python:3.6

EXPOSE 5000

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY threedeposit /app/threedeposit
COPY init_db.py /app

CMD ["python", "init_db.py"]

CMD flask run --host=0.0.0.0
