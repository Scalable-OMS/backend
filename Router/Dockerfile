FROM python

COPY ./requirements.txt ./requirements.txt

RUN mkdir src
COPY ./src ./src

RUN pip install -r requirements.txt

CMD ["python", "./src/router.py"]
