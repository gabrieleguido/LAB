FROM python:3.10-slim

# directory di lavoro del docker
WORKDIR /app

# copia le librerie dell'ambiente e le installa se non sono installate
COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copia cartelle "src" e "templates"
COPY src/ ./src/
COPY templates/ ./templates/

WORKDIR /app/src

EXPOSE 8004

CMD ["uvicorn", "frontend:app", "--host", "0.0.0.0", "--port", "8004"]