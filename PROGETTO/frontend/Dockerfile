FROM python:3.10

# directory di lavoro del docker
WORKDIR /app

# copia le librerie dell'ambiente e le installa se non sono installate
COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copia cartelle "src" e "templates"
COPY src/ ./src/
COPY templates/ ./templates/

EXPOSE 8004

CMD ["uvicorn", "src.frontend:app", "--host", "0.0.0.0", "--port", "8004"]