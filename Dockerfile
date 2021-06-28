FROM python:3

RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean

RUN mkdir /nur-bank
COPY . /nur-bank/
WORKDIR /nur-bank

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["main.py"]