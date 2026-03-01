import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='user1_to_user2')
channel.queue_declare(queue='user2_to_user1')

def callback(ch, method, properties, body):
    print(f"[User1] {body.decode()}")

channel.basic_consume(queue='user1_to_user2',
                      on_message_callback=callback,
                      auto_ack=True)

print("Chat dimulai. Ketik pesan untuk User1. CTRL+C untuk keluar.")
while True:
    message = input("User2: ")
    channel.basic_publish(exchange='',
                          routing_key='user2_to_user1',
                          body=message)
    channel.connection.process_data_events()
