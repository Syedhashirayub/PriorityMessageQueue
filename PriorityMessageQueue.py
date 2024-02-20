import queue
import threading
from concurrent.futures import ThreadPoolExecutor
import random

import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s [Thread %(thread)d]: %(message)s')

class PriorityMessageQueue:
    def __init__(self):
        self.queue = queue.PriorityQueue()
        self.condition = threading.Condition()  

    def enqueue_message(self, priority, message):
        with self.condition:  
            self.queue.put((priority, message))
            self.condition.notify()  

    def dequeue_message(self):
        with self.condition:
            while self.queue.empty():
                self.condition.wait()  
            return self.queue.get()[1] 

    def peek_message(self):
        with self.condition:
            if not self.queue.empty():
                return self.queue.queue[0][1]  
            return None

    def is_empty(self):
        with self.condition:
            return self.queue.empty()

def worker(message_queue):
    while True:
        message = message_queue.dequeue_message()
        if message is None:
            break
        logging.info(f"Processing message: {message}")


def enqueue_messages(message_queue, num_messages=100):
    for _ in range(num_messages):
        priority = random.randint(1, 10)
        message = f"Message with priority {priority}"
        message_queue.enqueue_message(priority, message)

def test_priority_collision(message_queue):
    print("Testing priority collision...")
    priorities = [5] * 10  
    for priority in priorities:
        message_queue.enqueue_message(priority, f"Collision message with priority {priority}")
    for _ in range(len(priorities)):
        print(message_queue.dequeue_message())

def test_empty_queue_dequeue(message_queue):
    print("Testing dequeue from empty queue...")
   
    threading.Thread(target=lambda: print(message_queue.dequeue_message())).start()

def test_peek_consistency(message_queue):
    print("Testing peek consistency...")
    message_queue.enqueue_message(2, "Initial top priority message")
    print("Peeked message:", message_queue.peek_message())
    message_queue.enqueue_message(1, "New top priority message")
    print("Peeked message after update:", message_queue.peek_message())

def main():
    NUM_THREADS = 4
    message_queue = PriorityMessageQueue()

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        # Testing concurrent enqueue and dequeue
        executor.submit(enqueue_messages, message_queue, 50)

        # Additional tests
        test_priority_collision(message_queue)
        test_empty_queue_dequeue(message_queue)
        test_peek_consistency(message_queue)

        # Start worker threads to process the enqueued messages
        for _ in range(NUM_THREADS):
            executor.submit(worker, message_queue)

        # Wait a bit before enqueuing to simulate random activity
        executor.submit(enqueue_messages, message_queue, 50)

if __name__ == "__main__":
    main()
