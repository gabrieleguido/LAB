FROM python:3.10-slim
WORKDIR /app
COPY domains.json .
COPY gs_data/ ./gs_data
WORKDIR /app/backend/src
COPY parser_wikipedia.py parser_weather.py cleaner.py token_compare.py . 
RUN pip install -r requirements.txt 
RUN crawl4ai-setup
COPY server.py 
EXPOSE 8003
CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8003"]