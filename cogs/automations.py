import interactions
from cogs.miscellaneous import log_message
from utils.yaml_file import id_map

class Automations(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    #region - MEMBER LISTENERS
    @interactions.listen()
    async def on_member_update(self, member_update: interactions.events.MemberUpdate):
        if member_update.before.pending and not member_update.after.pending:
            await member_update.after.add_role(id_map["member_role"])
            await log_message(self, f"{member_update.after.mention} accepterede reglerne.")

    @interactions.listen()
    async def on_member_add(self, member_add: interactions.events.MemberAdd):
        await log_message(self, f"**+** {member_add.member.username}")

    @interactions.listen()
    async def on_member_remove(self, member_remove: interactions.events.MemberRemove):
        await log_message(self, f"**-** *{member_remove.member.username}*")
    #endregion

def setup(client):
    Automations(client)
