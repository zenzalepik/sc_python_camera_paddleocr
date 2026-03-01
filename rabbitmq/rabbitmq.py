import pika

# Koneksi ke RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Pastikan queue ada
channel.queue_declare(queue='hello')

# Loop untuk input manual
while True:
    message = input("Ketik pesan (atau 'exit' untuk keluar): ")
    if message.lower() == "exit":
        break

    channel.basic_publish(exchange='',
                          routing_key='hello',
                          body=message)
    print(f" [x] Sent '{message}'")

connection.close()
