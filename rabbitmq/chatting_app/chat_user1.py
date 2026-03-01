import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='user1_to_user2')
channel.queue_declare(queue='user2_to_user1')

def callback(ch, method, properties, body):
    print(f"[User2] {body.decode()}")

channel.basic_consume(queue='user2_to_user1',
                      on_message_callback=callback,
                      auto_ack=True)

print("Chat dimulai. Ketik pesan untuk User2. CTRL+C untuk keluar.")
while True:
    message = input("User1: ")
    channel.basic_publish(exchange='',
                          routing_key='user1_to_user2',
                          body=message)
    channel.connection.process_data_events()
