from abc import ABC, abstractmethod


class RMQConsumerInterface(ABC):

    @staticmethod
    @abstractmethod
    async def callback(message):
        """
        Process the message received from the queue.
        This method needs to be implemented by the subclass.
        """
        pass

    @abstractmethod
    async def consume_messages(self):
        """
        Start consuming messages from the queue.
        This method needs to be implemented by the subclass.
        """
        pass
