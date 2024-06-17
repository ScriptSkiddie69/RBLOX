import roblox as rbx
import os
client = rbx.Client()
@client.set(id='Conversation_Id here', prefix='!', command="ping")
async def c1(*args):
    print('Pong!')

#Functions
#client.id { fetch client userid }
#client.name { fetch client name }
#client.can_mail(<int>) { return <BOOL>, Checks if client can mail that userid}
#client.send(<str>) { POST <STR>, Send messages }
#rbx.check_cookie(<STR>) { POST <STR>, Returns BOOL checks if cookie is valid or not}

client.run('ROBLOX COOKIE HERE')
