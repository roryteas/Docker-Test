FROM python:3.10

ADD server3.py .

ADD bippy.html .

RUN pip install pybase64 sockets thread6 pycurl time BytesIO sqlalchemy


CMD ["python", "./server3.py"]


