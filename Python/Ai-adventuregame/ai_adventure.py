from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.prompts  import  PromptTemplate
from langchain.chains import LLMChain
import json

# ADD YOUR OWN ZIP FOLDER OBTAINED WHILE CREATING THE VECTOR DATABASE OF ASTRA
cloud_config= {
  'secure_connect_bundle': 'secure-connect-choose-your-own-adventure.zip'
}


with open("choose_your_own_adventure-token.json") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]

# ADD YOUR ASTRA DATABASE NAME
ASTRA_DB_KEYSPACE = "database"

# ADD YOUR OPENAI API KEY 
OPENAI_API_KEY = "" 

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()


# CONFIG SETTINGS 

message_history = CassandraChatMessageHistory(
    session_id="anything",
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

# CUSTOM TEAMPLATE FOR OPEN AI 
template = """
You are now the game guide of a mystical journey in the Whispering Woods. You must ask the player for his or her name and address them with that name further in the game.
A player seeks the lost Gem of Serenity. 
You must navigate her through challenges, choices, and consequences, 
dynamically adapting the tale based on the traveler's decisions. The Game should go on with  plots and new characters being introduced further in the game either helping or opposing the player. 
Your goal is to create a branching narrative experience where each choice 
leads to a new path, ultimately determining the player's fate. 

Here are some rules to follow:
1. Start by asking the player their name and to choose some kind of weapons that will be used later in the game, keep the weapon theme medieval.
2. Have a few paths that lead to success
3. Have some paths that lead to death. If the user dies generate a response that explains the death and ends in the text: "The End.", I will search for this text to end the game
Here is the chat history, use this to understand what to say next: {chat_history}
Human: {human_input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

llm = OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)

choice = "start"

while True:
    response = llm_chain.predict(human_input=choice)
    print("\n")
    print("guide: ",response.strip())
    print("--------------------------------------------------------------------------------")
    print("\n")

    if "The End." in response:
        break

    choice = input("Your reply: ")