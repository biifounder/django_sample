import json
from channels.generic.websocket import AsyncWebsocketConsumer
import uuid

class QuizConsumer(AsyncWebsocketConsumer):
    # Dictionary to hold scores and state for each room.
    # Structure: {'room_name': {'scores': {}, 'current_question': {}, 'questions_sent': 0, 'answer_counts': {}, 'last_teacher_message': ''}}
    room_state = {}

    async def connect(self):
        
        try:
            self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default_room')
            self.room_group_name = f'quiz_{self.room_name}'
            # Use session key for unique student identification, or client IP as fallback
            self.user_id = self.scope['session'].session_key or str(uuid.uuid4())
            print(f"🔌 WebSocket connected for {self.user_id} in room {self.room_name}")
            
            # Initialize state for this room if it's the first connection.
            if self.room_name not in self.room_state:
                self.room_state[self.room_name] = {
                    'scores': {}, 
                    'current_question': {}, 
                    'questions_sent': 0,
                    'answer_counts': {},
                    'last_teacher_message': ''
                }
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send the last teacher message to the student upon joining
            if 'teacher' not in self.scope['path'] and self.room_state[self.room_name]['last_teacher_message']:
                await self.send(text_data=json.dumps({
                    'type': 'teacher_message_broadcast',
                    'content': self.room_state[self.room_name]['last_teacher_message']
                }))
                
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
            # Removed logic to automatically delete student scores on disconnect to keep scores stable
            
        except Exception as e:
            print(f"❌ Error during WebSocket disconnection: {e}")
            
        

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            
            message_type = text_data_json.get('type')
            message_content = text_data_json.get('content')
            
            if message_type == 'new_question':
                self.room_state[self.room_name]['current_question'] = message_content
                self.room_state[self.room_name]['questions_sent'] += 1
                
                # Reset answered_current_question flag for all students
                for user_id in self.room_state[self.room_name]['scores']:
                    self.room_state[self.room_name]['scores'][user_id]['answered_current_question'] = False
                
                # Reset answer counts for the new question
                self.room_state[self.room_name]['answer_counts'] = {option: 0 for option in message_content['options']}

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'quiz_question',
                        'content': message_content
                    }
                )

            elif message_type == 'student_answer':
                submitted_answer = message_content
                current_question_data = self.room_state[self.room_name]['current_question']
                
                if current_question_data and 'correct_answer' in current_question_data:
                    # Increment answered count
                    if self.user_id in self.room_state[self.room_name]['scores']:
                        self.room_state[self.room_name]['scores'][self.user_id]['answered'] += 1

                    # Update answer counts for this question
                    if submitted_answer in self.room_state[self.room_name]['answer_counts']:
                        self.room_state[self.room_name]['answer_counts'][submitted_answer] += 1
                    
                    if submitted_answer.strip() == current_question_data.get('correct_answer').strip():
                        # Check if the student has already answered the current question to avoid double-scoring
                        if self.user_id in self.room_state[self.room_name]['scores'] and not self.room_state[self.room_name]['scores'][self.user_id].get('answered_current_question'):
                            self.room_state[self.room_name]['scores'][self.user_id]['score'] += 1
                            self.room_state[self.room_name]['scores'][self.user_id]['answered_current_question'] = True
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'update_score',
                            'content': self.room_state[self.room_name]['scores']
                        }
                    )
                    
                    # Send question stats to the teacher
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'question_stats',
                            'content': {
                                'counts': self.room_state[self.room_name]['answer_counts'],
                                'correct_answer': current_question_data['correct_answer']
                            }
                        }
                    )

            elif message_type == 'student_join':
                student_name = message_content

                # Check if this name already exists in scores
                name_already_registered = any(
                    entry['name'] == student_name
                    for entry in self.room_state[self.room_name]['scores'].values()
                )

                if not name_already_registered:
                    # Register this user_id with the name
                    self.room_state[self.room_name]['scores'][self.user_id] = {
                        'name': student_name,
                        'score': 0,
                        'answered': 0,
                        'message_count': 0,
                        'answered_current_question': False
                    }

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'update_score',
                            'content': self.room_state[self.room_name]['scores']
                        }
                    )
                else:
                    # Optional: update existing entry with new user_id
                    for uid, entry in list(self.room_state[self.room_name]['scores'].items()): # Iterate over copy for safe deletion
                        if entry['name'] == student_name and uid != self.user_id:
                            # If a student with the same name connects again (likely same user with new ID),
                            # keep the data and link it to the new user_id, deleting the old entry if present
                            self.room_state[self.room_name]['scores'][self.user_id] = entry
                            if uid in self.room_state[self.room_name]['scores']:
                                del self.room_state[self.room_name]['scores'][uid]
                            break

            elif message_type == 'quiz_end':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'quiz_end',
                        'content': 'Quiz has ended.'
                    }
                )

            elif message_type == 'timer_pause':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'timer_pause',
                        'content': message_content
                    }
                )

            elif message_type == 'timer_resume':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'timer_resume',
                        'content': None
                    }
                )
            
            elif message_type == 'student_question':
                # Increment message count for a student question
                if self.user_id in self.room_state[self.room_name]['scores']:
                    self.room_state[self.room_name]['scores'][self.user_id]['message_count'] += 1
                
                # Send the student question message to the teacher
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'student_question',
                        'content': message_content
                    }
                )
                
                # Send an update_score message to also update the top table
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_score',
                        'content': self.room_state[self.room_name]['scores']
                    }
                )
            
            elif message_type == 'teacher_message':
                message = message_content.get('message')
                if message:
                    self.room_state[self.room_name]['last_teacher_message'] = message # Store the last message

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'teacher_message_broadcast',
                            'content': message
                        }
                    )
            elif message_type == 'hand_raise':
                print(f"✋ Received hand_raise from {message_content}")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'hand_raise',
                        'student': message_content
                    }
                )
            elif message_type == 'hand_lower':
                print(f"✋ Received hand_lower from {message_content}")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'hand_lower',
                        'student': message_content
                    }
                )

            elif message_type == 'remove_student':
                student_name = message_content

                # Find and remove all user_ids with this name
                to_remove = [uid for uid, entry in self.room_state[self.room_name]['scores'].items()
                            if entry['name'] == student_name]

                for uid in to_remove:
                    if uid in self.room_state[self.room_name]['scores']:
                         del self.room_state[self.room_name]['scores'][uid]

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_score',
                        'content': self.room_state[self.room_name]['scores']
                    }
                )

            elif message_type == 'student_math_steps':
                student_name = message_content.get('name')
                steps = message_content.get('steps', [])

                # Broadcast to all connected teacher clients
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'broadcast_math_steps',
                        'name': student_name,
                        'steps': steps
                    }
                )

            elif message_type == 'image_question':
                image_url = message_content.get('image_url')
                time_limit = message_content.get('time_limit', 60)

                self.room_state[self.room_name]['current_question'] = {
                    'image_url': image_url,
                    'time_limit': time_limit,
                    'correct_answer': '',
                    'options': []
                }

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'quiz_question',
                        'content': self.room_state[self.room_name]['current_question']
                    }
                )






        except json.JSONDecodeError:
            print("❌ Error: Received invalid JSON data.")
        except Exception as e:
            print(f"❌ An unexpected error occurred in the receive method: {e}")

    # Async handlers for group messages

    async def quiz_question(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'question',
                'content': event['content']
            }))
        except Exception as e:
            print(f"❌ Error sending question to client: {e}")

    async def update_score(self, event):
        try:
            # Calculate rank and include it for the student's personal view
            scores = event['content']
            sorted_students = sorted(scores.values(), key=lambda x: x['score'], reverse=True)
            
            # Find the rank of the current user
            rank = 1
            last_score = -1
            student_rank = '-'
            student_score = 0
            
            for index, student in enumerate(sorted_students):
                if student['score'] < last_score:
                    rank = index + 1
                
                if student.get('name') == self.room_state[self.room_name]['scores'].get(self.user_id, {}).get('name'):
                    student_rank = rank
                    student_score = student['score']
                    break
                
                last_score = student['score']


            await self.send(text_data=json.dumps({
                'type': 'update_score',
                'content': {
                    **event['content'], 
                    'score': student_score, # For student view
                    'rank': student_rank    # For student view
                }
            }))
        except Exception as e:
            print(f"❌ Error sending score update: {e}")

    async def question_stats(self, event):
        try:
            await self.send(text_data=json.dumps(event))
        except Exception as e:
            print(f"❌ Error sending question stats: {e}")
    
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
        except Exception as e:
            print(f"❌ Error sending timer_pause message: {e}")

    async def timer_resume(self, event):
        try:
            await self.send(text_data=json.dumps(event))
        except Exception as e:
            print(f"❌ Error sending timer_resume message: {e}")
    
    async def student_question(self, event):
        try:
            await self.send(text_data=json.dumps(event))
        except Exception as e:
            print(f"❌ Error sending student question: {e}")

    async def teacher_message_broadcast(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'teacher_message_broadcast',
                'content': event['content']
            }))
        except Exception as e:
            print(f"❌ Error sending teacher message: {e}")
    
    async def hand_raise(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'hand_raise',
                'student': event['student']
            }))
        except Exception as e:
            print(f"❌ Error broadcasting hand raise: {e}") 
            
    async def hand_lower(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'hand_lower',
                'student': event['student']
            }))                        
        except Exception as e:
            print(f"❌ Error broadcasting hand lower: {e}")

    async def broadcast_math_steps(self, event):
        await self.send(text_data=json.dumps({
            'type': 'student_math_steps',
            'content': {
                'name': event['name'],
                'steps': event['steps']
            }
        }))

            

# <!-- rearrange math pannels -->
# <!-- rearrange math pannels -->
# <!-- rearrange math pannels -->