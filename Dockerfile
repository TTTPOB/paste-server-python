FROM python:3.9-buster
WORKDIR /app
COPY requirements.txt .
COPY server.py .
RUN pip3 install -r requirements.txt
CMD ["python3", "-m", "uvicorn", "server:app", "--host", "0.0.0.0"]
