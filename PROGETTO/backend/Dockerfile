FROM python:3.10-slim
WORKDIR /app
COPY backend/ ./backend 
EXPOSE 8003
RUN pip install --no-cache-dir -r requirements.txt 
WORKDIR /app/backend/src
CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8003"]