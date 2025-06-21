import interactions, os
from dotenv import load_dotenv
from utils.database import DatabaseManager

load_dotenv()
db = DatabaseManager()

client = interactions.Client(
    intents = interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.GUILDS | interactions.Intents.MESSAGE_CONTENT,
    status = interactions.Status.ONLINE, delete_unused_application_cmds = True
)

@interactions.listen()
async def on_startup():
    await client.wait_until_ready()
    print(f"'{client.user.username}' is now online!")
    await db.create_pool()

@interactions.listen()
async def on_shutdown():
    print(f"'{client.user.username}' is shutting down...")
    await db.close_pool()

def load_extensions(folder_name: str):
    """ Load all bot extensions from the given directory. """
    for filename in os.listdir(f"./{folder_name}"):
        if filename.endswith(".py"):
            ext_name = f"{folder_name}.{filename[:-3]}"
            client.load_extension(ext_name)

if __name__ == "__main__":
    load_extensions("cogs")
    client.start(os.getenv("CLIENT_TOKEN"))
