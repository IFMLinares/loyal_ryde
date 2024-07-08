from channels.generic.websocket import WebsocketConsumer 


class NotificationConsummer(WebsocketConsumer):
    
    def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            return
        self.accept()

    def disconnect(self, close_code):
        pass


