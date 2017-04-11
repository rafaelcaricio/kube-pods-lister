FROM python:3.6

RUN pip install click
RUN pip install kubernetes

COPY pods_lister.py /
ENTRYPOINT ["python", "pods_lister.py"]
