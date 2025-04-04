FROM python:3.11

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ .

# nanoをインストール
# RUN apt-get update && apt-get install -y nano

CMD ["python", "main.py"]
# CMD [ "bash", "-c", "python get_2Auto.py && python main.py" ]
