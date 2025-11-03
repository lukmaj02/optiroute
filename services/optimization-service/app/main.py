import os
import uuid
import pika
import time
import csv
import json
from sqlalchemy import create_engine, Column, String, DateTime, JSON, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

# --- 1. Konfiguracja Bazy Danych (Identyczna jak w upload-service) ---

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres/db")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Model Job (Musi być identyczny!)
class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String, default="PENDING", index=True)
    input_file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    result = Column(JSON, nullable=True)

# Funkcja pomocnicza do pobierania sesji DB
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        # Worker działa inaczej niż API, więc inaczej zarządzamy sesją
        pass 

# --- 2. Konfiguracja RabbitMQ ---

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")
JOB_QUEUE = "job_queue"

# --- 3. Główna logika workera ---

def process_job(job_id):
    """
    Funkcja, która wykonuje całą logikę przetwarzania zlecenia.
    """
    db = get_db()
    try:
        print(f"[{job_id}] Rozpoczynam przetwarzanie...")
        
        # 1. Pobierz zadanie z bazy
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"[{job_id}] BŁĄD: Nie znaleziono zlecenia w bazie.")
            return

        # 2. Oznacz zadanie jako "PROCESSING"
        job.status = "PROCESSING"
        db.commit()

        # 3. Odczytaj plik CSV (z wolumenu /app/uploads)
        if not os.path.exists(job.input_file_path):
             raise FileNotFoundError(f"Plik {job.input_file_path} nie istnieje.")
        
        parsed_data = []
        with open(job.input_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Pomiń nagłówek, jeśli istnieje (do dostosowania)
            # next(reader, None) 
            for row in reader:
                parsed_data.append(row)
        
        print(f"[{job_id}] Przetworzono {len(parsed_data)} wierszy z CSV.")

        # --- MIEJSCE NA PRZYSZŁĄ LOGIKĘ ---
        # Tutaj w przyszłości:
        # 1. Wołanie geokodowania (Nominatim)
        # 2. Wołanie data-aggregator (pogoda, smog)
        # 3. Wołanie API TomTom Route Optimization
        # 4. Symulujemy pracę przez 3 sekundy
        time.sleep(3)
        # ------------------------------------

        # 4. Zapisz wynik (na razie tylko odczytane dane)
        job.status = "COMPLETED"
        job.result = {
            "message": "Trasa zoptymalizowana pomyślnie (symulacja)",
            "parsed_rows_count": len(parsed_data),
            "optimized_route": parsed_data # Na razie zwracamy to co odczytaliśmy
        }
        db.commit()
        print(f"[{job_id}] Zakończono pomyślnie.")

    except Exception as e:
        # 5. Obsługa błędów
        print(f"[{job_id}] BŁĄD KRYTYCZNY: {e}")
        if db.is_active:
            db.rollback()
        job.status = "FAILED"
        job.result = {"error": str(e)}
        db.commit()
    finally:
        db.close()

def main():
    # Czekaj na RabbitMQ i połącz się
    connection = None
    while not connection:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        except pika.exceptions.AMQPConnectionError:
            print("Czekam na RabbitMQ...")
            time.sleep(2)

    channel = connection.channel()
    channel.queue_declare(queue=JOB_QUEUE, durable=True)
    print('[*] Czekam na zlecenia. Naciśnij CTRL+C aby wyjść.')

    # Funkcja callback - co ma się stać, gdy przyjdzie wiadomość
    def callback(ch, method, properties, body):
        job_id_str = body.decode()
        
        try:
            # Próbuj konwertować na UUID (dla pewności)
            job_id = uuid.UUID(job_id_str)
            print(f"[+] Otrzymano zlecenie: {job_id}")
            process_job(job_id)
        except ValueError:
            print(f"[!] Otrzymano błędny job_id: {job_id_str}")
        except Exception as e:
            print(f"[!] Nieoczekiwany błąd podczas process_job: {e}")
        
        # Potwierdź RabbitMQ, że wiadomość została przetworzona
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # Powiedz RabbitMQ, aby wysyłał do tego workera tylko jedną wiadomość na raz
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=JOB_QUEUE, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Zamykanie...")
        channel.stop_consuming()
        connection.close()

if __name__ == '__main__':
    # Upewnij się, że tabela 'jobs' istnieje, zanim worker wystartuje
    time.sleep(5) # Daj postgresowi chwilę
    Base.metadata.create_all(bind=engine)
    main()