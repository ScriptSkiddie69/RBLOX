import requests
import json
import asyncio
# API endpoints and settings
apis = {
    "roblox": {
        "send-messages": "https://apis.roblox.com/platform-chat-api/v1/send-messages",
        "get-messages": "https://apis.roblox.com/platform-chat-api/v1/get-conversation-messages",
        "send-mail": "https://privatemessages.roblox.com/v1/messages/send",
        "create-conversations": "https://apis.roblox.com/platform-chat-api/v1/create-conversations"
    }
}

settings = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "cookie": "" 
}

headers = {
    "User-Agent": settings['user_agent'],
    "Content-Type": "application/json",
    "X-Csrf-Token": None
}

stuff = {
    "id": None
}
def check_cookie(cookie):
    try:
        r = requests.post("https://auth.roblox.com/v2/logout", headers=headers, cookies={'.ROBLOSECURITY': cookie})
        response_data = r.json()
        if 'errors' in response_data and isinstance(response_data['errors'], list):
            for error in response_data['errors']:
                if error.get('code') == 0:
                    return "Invalid cookie found!"
            return "Valid cookie"
        else:
            return "Valid cookie"
    except json.JSONDecodeError:
        return "Error decoding JSON response"
    except Exception as e:
        return f"Error occurred: {e}"


def fetch(type):
    if type == "csrf":
        try:
            r = requests.post("https://auth.roblox.com/v2/logout", headers=headers, cookies={'.ROBLOSECURITY': settings['cookie']})
            return r.headers.get('x-csrf-token')
        except Exception as e:
            return f"Error occurred: {e}"
    elif type == "id":
        try:
            r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers, cookies={'.ROBLOSECURITY': settings['cookie']})
            return json.loads(r.text)['id']
        except Exception as e:
            return f"Error occurred: {e}"

def create_request(request, *args):
    #headers['X-Csrf-Token'] = fetch('csrf')
    try:
        if request == "Message":
            data = {"conversation_id": args[0], "messages": [{"content": args[1]}]}
            req = requests.post(apis['roblox']['send-messages'], headers=headers, json=data, cookies={'.ROBLOSECURITY': settings['cookie']})
            print(req.text)
            return req.text
        elif request == "Group":
            wtf = args[0]
            if len(args) > 0:
                args_list = list(args)
                args_list.pop(0)
                data = {"conversations": [{"type": "group", "name": wtf, "participant_user_ids": args_list}]}
                req = requests.post(apis['roblox']['create-conversations'], headers=headers, json=data, cookies={'.ROBLOSECURITY': settings['cookie']})
                return req.text
        elif request == "Mail":
            data = {"subject": args[0], "body": args[1], "recipientid": args[2], "cacheBuster": 1718289343323}
            req = requests.post(apis['roblox']['send-mail'], headers=headers, json=data, cookies={'.ROBLOSECURITY': settings['cookie']})
            return req.text
        else:
            return "Invalid request type"
    except Exception as e:
        return f"Error occurred: {e}"


def get_message(cid):
    try:
        params = {"conversation_id": cid, "pageSize": 3}
        req = requests.get(apis['roblox']['get-messages'], params=params, cookies={'.ROBLOSECURITY': settings['cookie']})
        return req.text
    except Exception as e:
        return f"Error occurred: {e}"


class Client:
    def __init__(self):
        self.commands = {}
        self.vars = {"latest": None}
        self._name = None
        self._id = None

    def set(self, id, prefix, command):
        def decorator(func):
            self.commands[command] = {
                'func': func,
                'id': id,
                'prefix': prefix
            }
            return func
        return decorator

    def receive_message(self, conversation_id):
        msg = get_message(conversation_id)
        try:
            message_data = json.loads(msg)
            if 'messages' not in message_data or len(message_data['messages']) == 0:
                raise ValueError(f"No messages found in conversation ID: {conversation_id}")
            latest = message_data['messages'][0]['created_at']
            content = message_data['messages'][0]['content']
            return content, latest
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            #print(f"Error parsing message data for conversation ID {conversation_id}: {e}")
            return None, None

    async def _process_command(self, user_input, command_info):
        if user_input.strip().lower() == 'quit':
            return False

        parts = user_input.strip().split(' ', 1)
        if len(parts) == 0:
            return True

        command_name = parts[0][1:]
        if len(parts) > 1:
            args = [arg.strip() for arg in parts[1].split(',')]
        else:
            args = []

        if command_name in self.commands:
            command = self.commands[command_name]
            if (command['id'] == command_info['id'] and 
                command['prefix'] == parts[0][0]): 
                stuff['id'] = command_info['id']
                func = command['func']
                func_args = []
                for i in range(func.__code__.co_argcount):
                    if i < len(args):
                        func_args.append(args[i])
                    else:
                        func_args.append(None)
                await func(*func_args)

            #else:
             #   print(f"Invalid command format or conversation ID: {user_input}")
        #else:
        #    print(f"Command '{command_name}' not found.")

        return True

    def can_mail(self, id):
        try:
            r = requests.get(f"https://privatemessages.roblox.com/v1/messages/{id}/can-message", headers=headers, cookies={'.ROBLOSECURITY': settings['cookie']})
            r.raise_for_status() 
            return json.loads(r.text).get('canMessage', False)
        except requests.RequestException as e:
            print(f"Request error: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except KeyError as e:
            print(f"Key error: {e}")
        return False
    def name(self):
        print(settings['cookie'])
        r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers, cookies={'.ROBLOSECURITY': settings['cookie']})

        return json.loads(r.text)['displayName']

    def id(self):
        r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers, cookies={'.ROBLOSECURITY': settings['cookie']})
        print(settings['cookie'])
        return json.loads(r.text)['id']

    def send(self, message):
        print(stuff['id'])
        create_request('Message', stuff['id'], message)

    def create_group(self, name, *members):
        create_request('Group' , name, members)

    def send_mail(self, subject, body, recipientid):
        create_request('Mail', subject, body, recipientid)

    async def _main(self):
        #print(check_cookie(token))
        processed_messages = set()
        headers['X-Csrf-Token'] = fetch('csrf')
        print(headers['X-Csrf-Token'])
        #print(check_cookie(token))
        while True:
            for command_name, command_info in self.commands.items():
                user_input, latest_message_time = self.receive_message(command_info['id'])
                if user_input is None or latest_message_time is None:
                    await asyncio.sleep(1)
                    continue

                if latest_message_time in processed_messages:
                    continue

                if self.vars['latest'] != latest_message_time:
                    self.vars['latest'] = latest_message_time
                    continue_processing = await self._process_command(user_input, command_info)

                    if not continue_processing:
                        return

                    processed_messages.add(latest_message_time)


    def run(self, token):
        settings['cookie'] = token
        print(check_cookie(token))

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._main())
        finally:
            loop.close()
if __name__ == "__main__":
    print(check_cookie())
    r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers, cookies={'.ROBLOSECURITY': settings['cookie']})
    Client.self._id = json.loads(r.text)['id']
    r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers, cookies={'.ROBLOSECURITY': settings['cookie']})
    Client.self._name = json.loads(r.text)['displayName']

    # Example: create_request("Message", conversation_id, "Hello!")
    # Example: create_request("Group", "group_name", participant_user_ids)
    # Example: create_request("Mail", "subject", "body", "recipient_id")
    # Example: receive_message(conversation_id)

