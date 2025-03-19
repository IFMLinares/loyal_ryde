import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

class NotificationConsummer(WebsocketConsumer):
    
    def connect(self):
        user = self.scope['user']
        print(f"Usuario conectado: {user}, autenticado: {user.is_authenticated}")
        if not user.is_authenticated:
            self.close()
            return

        self.username = user.username

        # Agregar al grupo del usuario
        async_to_sync(self.channel_layer.group_add)(
            self.username, self.channel_name
        )
        self.accept()

        # Enviar un mensaje de confirmación al cliente
        self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": f"Conexión establecida para el usuario {self.username}"
        }))
    
    def disconnect(self, close_code):
        # Leave room/group
        async_to_sync(self.channel_layer.group_discard )(
            self.username, self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Mensaje recibido: {data}")

        if data.get("type") == "subscribe":
            # Confirmar la suscripción del cliente
            self.send(text_data=json.dumps({
                "type": "subscription_confirmed",
                "message": f"Suscripción confirmada para el usuario {self.username}"
            }))
    
    def send_group(self, group, source, data):
        response = {
            'type': 'broadcast_group',
            'source': source,
            'data': data
        }
        async_to_sync(self.channel_layer.group_send)(
            group, response
        )

    def broadcast_group(self, data):
        '''
            data:
                - type 'broad_cast_group'
                - source 'where it originated from
                - data what ever you want to send as dict
        '''
        self.send(text_data=json(json.dumps(data)))
        '''
            return data:
                - soruce: where it originated from
                - data what ever you want to send as dict
        '''

    def transferencia_validada(self, event):
        transferencia_id = event["transferencia_id"]
        transferencia_data = event["transferencia_data"]
        rates = event["rates"]

        try:
            # Deserializamos los datos de transferencia
            transferencia_dict = json.loads(transferencia_data)
            transferencia_dict["rates"] = rates

            # Enviamos el JSON completo al cliente (conductor)
            response_data = {
                "type": "transferencia_validada",
                "source": "NotificationConsummer.transfer.accept",
                "data": transferencia_dict,
            }
            print(response_data)
            self.send(text_data=json.dumps(response_data))
        except (ValueError, IndexError, KeyError):
            # Manejamos errores de deserialización o campos faltantes
            error_message = f"Error al procesar la transferencia {transferencia_id}"
            print('D A T O S :')
            # print(transferencia_data)
            print(json.loads(transferencia_data))
            self.send(text_data=json.dumps({"error": error_message}))

class ConductorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Asocia al usuario al canal
        await self.accept()

    async def disconnect(self, close_code):
        # Lógica al desconectar (si es necesario)
        pass

    async def transferencia_validada(self, event):
        transferencia_id = event["transferencia_id"]
        # Aquí puedes enviar la ID de la transferencia al cliente (conductor)
        await self.send(text_data=f"Transferencia validada: {transferencia_id}")

class SiteNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'site_notifications'
        print(f"Conectando al grupo: {self.group_name}")
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Elimina al usuario del grupo de WebSocket
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        print("Mensaje recibido en el Consumer:", event)
        # Envía la notificación al cliente
        await self.send(text_data=json.dumps(event['message']))