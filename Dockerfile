# ベースイメージ（Python 3.11）
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY src/ .

# FastAPIアプリを起動（uvicorn）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
