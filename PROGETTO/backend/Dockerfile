FROM python:3.10-slim
WORKDIR /app
COPY domains.json .
COPY gs_data/ ./gs_data
COPY backend/ ./backend
WORKDIR /app/backend/
RUN pip install --no-cache-dir -r requirements.txt 
RUN crawl4ai-setup
WORKDIR /app/backend/src 
EXPOSE 8003
CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8003"]