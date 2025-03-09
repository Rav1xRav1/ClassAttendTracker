FROM postgres:latest

# init.sqlファイルをコンテナの/docker-entrypoint-initdb.dにコピー
# COPY ./init.sql /docker-entrypoint-initdb.d/
# COPY ./insert_data.sql /docker-entrypoint-initdb.d/insert_data.sql

# データベースのデータを保存するディレクトリ
COPY ./pg_data/ /var/lib/postgresql/data
