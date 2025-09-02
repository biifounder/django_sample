import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QuizConsumer(AsyncWebsocketConsumer):
    # Dictionary to hold scores for each room and the current question.
    # Structure: {'room_name': {'scores': {'user_id': {'name': 'Name', 'score': 0}}, 'current_question': {}}}
    room_state = {}

    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default_room')
            self.room_group_name = f'quiz_{self.room_name}'
            
            # Initialize state for this room if it's the first connection.
            if self.room_name not in self.room_state:
                self.room_state[self.room_name] = {'scores': {}, 'current_question': {}}
            
            self.user_id = self.scope['session'].session_key or self.scope['client'][0]
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            print(f"✅ WebSocket connection established for room: {self.room_group_name}")
        except Exception as e:
            print(f"❌ Error during WebSocket connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            print(f"🚪 WebSocket connection disconnected for room: {self.room_group_name} with code: {close_code}")
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"❌ Error during WebSocket disconnection: {e}")

    async def receive(self, text_data):
        try:
            print(f"Received raw data: {text_data}")
            text_data_json = json.loads(text_data)
            
            message_type = text_data_json.get('type')
            message_content = text_data_json.get('content')
            
            if message_type == 'new_question':
                self.room_state[self.room_name]['current_question'] = message_content
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'quiz_question',
                        'content': message_content
                    }
                )

            elif message_type == 'student_answer':
                submitted_answer = message_content
                current_question = self.room_state[self.room_name]['current_question']
                
                if current_question and submitted_answer == current_question.get('correct_answer'):
                    if self.user_id in self.room_state[self.room_name]['scores']:
                        self.room_state[self.room_name]['scores'][self.user_id]['score'] += 1
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'update_score',
                                'content': self.room_state[self.room_name]['scores']
                            }
                        )
            
            elif message_type == 'student_join':
                print(f"Student '{message_content}' joined the room.")
                self.room_state[self.room_name]['scores'][self.user_id] = {'name': message_content, 'score': 0}
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_score',
                        'content': self.room_state[self.room_name]['scores']
                    }
                )

            elif message_type == 'quiz_end':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'quiz_end',
                        'content': 'Quiz has ended.'
                    }
                )

            elif message_type == 'timer_pause':
                print(f"Received timer pause signal from teacher.")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'timer_pause',
                        'content': message_content
                    }
                )

            elif message_type == 'timer_resume':
                print(f"Received timer resume signal from teacher.")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'timer_resume',
                        'content': None
                    }
                )
            
            elif message_type == 'student_question':
                print(f"Received question from student {message_content['name']}.")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'student_question',
                        'content': message_content
                    }
                )

        except json.JSONDecodeError:
            print("❌ Error: Received invalid JSON data.")
        except Exception as e:
            print(f"❌ An unexpected error occurred in the receive method: {e}")

    async def quiz_question(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'question',
                'content': event['content']
            }))
            print(f"✅ Sent question to client: {event['content']['question_text']}")
        except Exception as e:
            print(f"❌ Error sending question to client: {e}")

    async def update_score(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'update_score',
                'content': event['content']
            }))
        except Exception as e:
            print(f"❌ Error sending score update: {e}")

    async def quiz_end(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'quiz_end',
                'content': event['content']
            }))
        except Exception as e:
            print(f"❌ Error sending quiz end message: {e}")

    async def timer_pause(self, event):
        try:
            await self.send(text_data=json.dumps(event))
            print("✅ Sent timer_pause signal to client.")
        except Exception as e:
            print(f"❌ Error sending timer_pause message: {e}")

    async def timer_resume(self, event):
        try:
            await self.send(text_data=json.dumps(event))
            print("✅ Sent timer_resume signal to client.")
        except Exception as e:
            print(f"❌ Error sending timer_resume message: {e}")
    
    async def student_question(self, event):
        try:
            await self.send(text_data=json.dumps(event))
            print("✅ Sent student question to client.")
        except Exception as e:
            print(f"❌ Error sending student question: {e}")