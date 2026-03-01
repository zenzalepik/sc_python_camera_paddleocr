import pika
import threading

USERNAME = input("Masukkan username: ")

def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='chat')

    def callback(ch, method, properties, body):
        # tampilkan pesan dari user lain
        print(f"\n{body.decode()}")
        print("Ketik pesan: ", end="", flush=True)

    channel.basic_consume(queue='chat',
                          on_message_callback=callback,
                          auto_ack=True)

    print(" [*] Menunggu pesan... CTRL+C untuk keluar")
    channel.start_consuming()

def produce():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='chat')

    while True:
        message = input("Ketik pesan: ")
        full_message = f"[{USERNAME}] {message}"
        channel.basic_publish(exchange='',
                              routing_key='chat',
                              body=full_message)
        print(f"[x] Sent: {full_message}")

# Jalankan consumer di thread terpisah
threading.Thread(target=consume, daemon=True).start()

# Jalankan producer di main thread
produce()
