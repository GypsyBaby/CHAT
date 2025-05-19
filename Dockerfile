FROM python:3.9
WORKDIR /code
ENV PYTHONPATH=/code
ENV DMITRIEV_CHAT_ENV=local
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/src
EXPOSE 8000
CMD ["python3.9", "src/app.py"]
