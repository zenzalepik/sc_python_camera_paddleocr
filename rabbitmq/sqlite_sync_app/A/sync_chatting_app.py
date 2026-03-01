import pika
import sqlite3
import threading
import json
import time
from datetime import datetime

USERNAME = input("Masukkan username: ")

# --- Setup SQLite ---
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()
conn_lock = threading.Lock()

# Tabel messages dengan UNIQUE constraint untuk mencegah duplikasi
cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    text TEXT,
    timestamp TEXT,
    UNIQUE(username, timestamp, text)
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    joined_at TEXT
)""")
conn.commit()

# --- Consumer ---
def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=600))
    channel = connection.channel()
    
    # Gunakan Fanout Exchange untuk broadcast
    channel.exchange_declare(exchange='chat_exchange', exchange_type='fanout', durable=True)
    
    # Buat queue unik untuk tiap client (auto-delete)
    result = channel.queue_declare(queue='', exclusive=True, auto_delete=True)
    queue_name = result.method.queue
    
    # Bind queue ke exchange
    channel.queue_bind(exchange='chat_exchange', queue=queue_name)

    def callback(ch, method, properties, body):
        try:
            event = json.loads(body.decode())
            
            if event["type"] == "message" and event["action"] == "create":
                with conn_lock:
                    cursor.execute("INSERT OR IGNORE INTO messages (username, text, timestamp) VALUES (?, ?, ?)",
                                   (event["sender"], event["text"], event["timestamp"]))
                    conn.commit()
                print(f"\n[{event['sender']}] {event['text']}")
                print("Ketik pesan: ", end="", flush=True)

            elif event["type"] == "user" and event["action"] == "create":
                with conn_lock:
                    cursor.execute("INSERT OR IGNORE INTO users (username, joined_at) VALUES (?, ?)",
                                   (event["sender"], event["joined_at"]))
                    conn.commit()
                print(f"\n[INFO] User baru terdaftar: {event['sender']}")
        except Exception as e:
            print(f"[ERROR] Callback error: {e}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(" [*] Menunggu pesan...")

    # Non-blocking consume
    while True:
        try:
            channel.connection.process_data_events(time_limit=1)
        except:
            break

    connection.close()

# --- Producer ---
def produce():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=600))
    channel = connection.channel()
    
    # Gunakan Fanout Exchange untuk broadcast
    channel.exchange_declare(exchange='chat_exchange', exchange_type='fanout', durable=True)

    # register user
    user_event = {
        "action": "create",
        "type": "user",
        "sender": USERNAME,
        "joined_at": datetime.now().isoformat()
    }
    channel.basic_publish(exchange='chat_exchange',
                          routing_key='',
                          body=json.dumps(user_event),
                          properties=pika.BasicProperties(delivery_mode=2))
    print(f"[INFO] Registered user: {USERNAME}")

    while True:
        try:
            message = input("Ketik pesan: ")
            event = {
                "action": "create",
                "type": "message",
                "sender": USERNAME,
                "text": message,
                "timestamp": datetime.now().isoformat()
            }
            channel.basic_publish(exchange='chat_exchange',
                                  routing_key='',
                                  body=json.dumps(event),
                                  properties=pika.BasicProperties(delivery_mode=2))
            print(f"[x] Sent: {event}")
        except EOFError:
            break

    connection.close()

# --- Run ---
print(f"\n=== Chat Client Started (User: {USERNAME}) ===")

# Start consumer thread
consumer_thread = threading.Thread(target=consume, daemon=True)
consumer_thread.start()

# Tunggu consumer siap
time.sleep(1)

# Jalankan producer
produce()
