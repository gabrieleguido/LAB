FROM python:3.10-slim
WORKDIR /app
COPY domains.json .
COPY gs_data/ ./gs_data/
RUN apt-get update -y
RUN apt-get install -y gcc libmariadb-dev
COPY backend/requirements.txt ./backend/
RUN pip install --upgrade pip 
RUN pip install -r ./backend/requirements.txt 
WORKDIR /app/backend/src
RUN crawl4ai-setup
COPY backend/src/ ./
EXPOSE 8003
CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8003"]