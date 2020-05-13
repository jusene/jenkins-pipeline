FROM python:3.7



COPY app /app

RUN pip install -r /app/requirement.txt 

CMD ["python", "/app/app.py"] 
