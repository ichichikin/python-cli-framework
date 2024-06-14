import pika
from classes.log import Log


class Amqp:
    def __init__(self, endpoint: str = "localhost", queue: str = "default", length: int = 10, purge: bool = False):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(endpoint, heartbeat=0))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=True)
        # self.channel.queue_declare(queue=queue, durable=True, arguments={'x-max-length': length})
        if purge:
            self.channel.queue_purge(queue)
        self.length = length
        self.queue = queue

    def get_str(self) -> str:
        res = self.channel.basic_get(queue=self.queue, auto_ack=True)[2]
        if isinstance(res, (bytes, bytearray)):
            return str(res, "utf-8")
        else:
            return res

    def get_byte(self) -> bytes:
        res = self.channel.basic_get(queue=self.queue, auto_ack=True)[2]
        return bytes(res) if res else bytes()

    def push(self, message: bytes) -> None:
        self.channel.basic_publish(exchange='', routing_key=self.queue, body=message)

    def purge(self) -> None:
        self.channel.queue_purge(queue=self.queue)

    def close(self):
        try:
            self.connection.close()
        except:
            pass
