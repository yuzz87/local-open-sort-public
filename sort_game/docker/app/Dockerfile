FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN g++ -std=c++17 cpp_engine/sort_engine.cpp cpp_engine/algorithms/*.cpp -O2 -o cpp_engine/sort_engine \
    && chmod +x cpp_engine/sort_engine

CMD ["python", "run.py"]