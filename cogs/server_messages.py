import interactions
from utils.trie import Trie
from utils.yaml_file import server_id

INVITE_LINK = "https://discord.gg/GJyyjrurHj"

RULES_DANISH = interactions.Embed(
    color = int("0x2f3136", 0),
    description = ("<:chatwitt:1048944473675137054>  | ChatWitt - Rules |  <:chatwitt:1048944473675137054>\n\n"
        "**§1** - Følg [Discords Community Guidelines.](https://discord.com/guidelines)\n\n"
        "**§2** - Trusler og chikane af enhver art er strengt forbudt.\n\n"
        "**§3** - Offentliggørelse af private data er ikke tilladt.\n\n"
        "**§4** - Fornærmelser, spam og upassende adfærd er forbudt.\n\n"
        "**§5** - Brug de relevante kanaler og hold dig til emnet.\n\n"
    )
)

class ServerMessages(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

        self._messages = {
            "welcome": self.welcome,
            "rules": self.rules
        }
        self.trie = Trie()
        for name in self._messages:
            self.trie.insert(name)

    #region - SSM (Send Server Message) COMMAND
    @interactions.slash_command(name = "ssm", description = "(Send Server Message) - send a server message",
        default_member_permissions = interactions.Permissions.ADMINISTRATOR, scopes = [server_id])
    @interactions.slash_option(name = "cmd", description = "choose the server message", opt_type = interactions.OptionType.STRING,
        required = True, autocomplete = True)
    @interactions.slash_option(name = "message_id", description = "message id to edit", opt_type = interactions.OptionType.STRING)
    async def ssm(self, ctx: interactions.SlashContext, cmd: str, message_id: str = None):
        handler = self._messages[cmd]
        if callable(handler):
            if message_id and cmd not in {"welcome", "rules"}:
                return await ctx.send(f"`{cmd}` cannot use a message ID!", ephemeral = True)
            await handler(ctx, message_id)
        else:
            await ctx.send("Command is not callable!", ephemeral = True)

    @ssm.autocomplete("cmd")
    async def __ssm_autocomplete(self, ctx: interactions.AutocompleteContext):
        input = ctx.input_text or ""
        if not input:
            await ctx.send(choices = [
                {"name": name.replace("_", " "), "value": name} for name in self._messages
            ])
            return
        # Search the Trie for commands matching the user's input
        match = self.trie.search(input.lower())
        limit = min(25, len(self._messages), len(match))
        await ctx.send(choices = [
            {"name": name, "value": name} for name in match[:limit]
        ])
    #endregion

    #region - WELCOME COMMAND
    async def welcome(self, ctx: interactions.SlashContext, message_id: str = None):
        welcome_message = ("# Velkommen til ChatWitt!\n\n"
            f"Discord invite link: {INVITE_LINK}")
        await self._send_or_edit_message(ctx, message_id, content = welcome_message)
    #endregion

    #region - RULES COMMAND
    async def rules(self, ctx: interactions.SlashContext, message_id: str = None):
        RULES_DANISH.set_footer("ChatWitt | Rules", ctx.guild.icon._url)
        await self._send_or_edit_message(ctx, message_id, embeds = RULES_DANISH)
    #endregion

    async def _send_or_edit_message(self, ctx: interactions.SlashContext, message_id: str, content: str = "", embeds: interactions.Embed = None):
        if message_id:
            try:
                message = await ctx.channel.fetch_message(int(message_id))
                await message.edit(content = content, embeds = embeds)
                msg = await ctx.send("_Message has been updated._", ephemeral = True)
                await ctx.delete(msg.id)
            except:
                await ctx.send("Failed to edit the message. Ensure the ID is correct.", ephemeral = True)
        else:
            await ctx.channel.send(content, embeds = embeds)
            msg = await ctx.send("_The message has been sent._", ephemeral = True)
            await ctx.delete(msg.id)

def setup(client):
    ServerMessages(client)
