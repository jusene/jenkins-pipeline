FROM python:3.7
MAINTAINER zj-huawei


COPY app /app

RUN pip install -r /app/requirement.txt 

CMD ["python", "/app/app.py"] 
