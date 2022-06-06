FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /src

COPY requirements.txt /src

RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python
RUN pip install sqlalchemy-hana
RUN pip install hdbcli

COPY . /src

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "80"]
