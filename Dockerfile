FROM python:3.10

ADD server3.py .

ADD /Front-End/functions.js .

ADD /Front-End/portfolio.html .

ADD portfolio.json .

ADD /Front-End/styles.css .



RUN pip install pybase64 sockets thread6 pycurl 

CMD ["python", "./server3.py"]


