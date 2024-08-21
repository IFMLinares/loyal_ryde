import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

class NotificationConsummer(WebsocketConsumer):
    
    def connect(self):
        user = self.scope['user']
        print(user, user.is_authenticated)
        if not user.is_authenticated:
            return
        self.username = user.username

        # Save username too use group name for this user

        async_to_sync(self.channel_layer.group_add)(
            self.username, self.channel_name
        )
        self.accept()
    
    def disconnect(self, close_code):
        
        # Leave room/group
        async_to_sync(self.channel_layer.group_discard )(
            self.username, self.channel_name
        )

    def receive(self, text_data):
        # receive mesasge from websocket
        data = json.loads(text_data)

        print('receive', json.dumps(data, index=2))
    
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
            transferencia_dict = json.loads(transferencia_data)[0]
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
            print(transferencia_data)
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
