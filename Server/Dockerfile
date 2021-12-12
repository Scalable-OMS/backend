FROM python

COPY ./requirements.txt ./requirements.txt
COPY ./wsgi.py ./wsgi.py

RUN mkdir app
COPY ./app/ ./app/

RUN pip install -r requirements.txt

EXPOSE 4000
CMD ["python", "./wsgi.py"]
