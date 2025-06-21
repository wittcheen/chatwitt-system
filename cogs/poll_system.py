import interactions
from dataclasses import dataclass, field
from cogs.miscellaneous import log_message
from utils.yaml_file import server_id

@dataclass
class Poll:
    title: str
    options: list[str]
    votes: dict[int, int] = field(default_factory = dict)

POLLS: dict[int, Poll] = {}
NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
END_POLL_EMOJI = "🔴"

POLL_MODAL = interactions.Modal(
    custom_id = "poll_form", title = "Create a new poll",
    *[interactions.InputText(
        custom_id = "title", required = True, min_length = 1, max_length = 100,
        style = interactions.TextStyles.SHORT, label = "Title:"
    ),interactions.InputText(
        custom_id = "options", required = True, min_length = 1, max_length = 3500,
        style = interactions.TextStyles.PARAGRAPH, label = "Poll options (min: 2, max: 10):", placeholder = "One option per line."
    )]
)

class PollSystem(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

    @interactions.slash_command(name = "poll", description = "create a new poll",
        default_member_permissions = interactions.Permissions.MANAGE_MESSAGES, scopes = [server_id])
    async def poll(self, ctx: interactions.SlashContext):
        await ctx.send_modal(POLL_MODAL)

    @interactions.modal_callback("poll_form")
    async def __poll_modal_response(self, ctx: interactions.ModalContext, title: str, options: str):
        _options = [option.strip() for option in options.split("\n") if option.strip()]
        num = len(_options)
        if num > len(NUMBERS):
            await ctx.send(f"This poll have to many options ({num}, max: {len(NUMBERS)}).", ephemeral = True)
        elif num < 2:
            await ctx.send(f"This poll doesn't have enough options ({num}, min: 2).", ephemeral = True)
        else:
            poll = Poll(title, options = _options)
            message = await ctx.send("_Loading.._")
            POLLS[int(message.id)] = poll
            select_menu = interactions.StringSelectMenu(
                custom_id = "poll_select",
                *[interactions.StringSelectOption(
                    label = choice, value = str(i),
                    emoji = interactions.PartialEmoji(name = NUMBERS[i])
                ) for i, choice in enumerate(poll.options)],
                placeholder = poll.title
            )
            embed = self.__create_embed(poll)
            embed.set_footer("ChatWitt | Poll", ctx.guild.icon._url)
            await message.edit(content = "", embeds = embed, components = select_menu)
            await ctx.send(f"The poll has been made. React with {END_POLL_EMOJI} to end the poll!", ephemeral = True)

    @interactions.component_callback("poll_select")
    async def __poll_select_response(self, ctx: interactions.ComponentContext):
        option = int(ctx.values[0])
        voter_id = int(ctx.author.id)
        poll = POLLS.get(int(ctx.message.id))
        if not poll:
            await self.close_poll(ctx.message)
        else:
            poll.votes[voter_id] = option
            embed = self.__create_embed(poll)
            embed.set_footer("ChatWitt | Poll", ctx.guild.icon._url)
            await ctx.message.edit(embeds = embed, components = ctx.message.components)
            await ctx.send(f"_Dit valg_: {NUMBERS[option]} • `{poll.options[option]}`", ephemeral = True)

    def __create_embed(self, poll: Poll) -> interactions.Embed:
        votes = [0] * len(poll.options)
        for option in poll.votes.values():
            votes[option] += 1
        num_votes = len(poll.votes)
        percentages = [round(vote / num_votes * 100, 2) if num_votes else 0 for vote in votes]
        bars = ["█" * round(percentage * 20 / 100) for percentage in percentages]
        fields = [(
            f"{NUMBERS[i]} - {choice}",
            f"{bars[i]} **{percentages[i]}%** ({votes[i]})"
        ) for i, choice in enumerate(poll.options)]
        embed = interactions.Embed(
            color = int("0x2f3136", 0),
            description = ("<:chatwitt:1048944473675137054>  | ChatWitt - Poll |  <:chatwitt:1048944473675137054>\n\n"
                f"**{poll.title}**\n\U00002800"
            )
        )
        for name, value in fields:
            embed.add_field(name, value)
        return embed

    async def close_poll(self, message: interactions.Message):
        embed = message.embeds[0]
        embed.add_field("\U00002800", "Denne poll er afsluttet")
        await message.edit(embeds = embed, components = [])

    @interactions.listen()
    async def on_message_reaction_add(self, message_reaction: interactions.events.MessageReactionAdd):
        poll_id = int(message_reaction.message.id)
        poll = POLLS.get(poll_id)
        if not poll:
            return
        if message_reaction.author.has_permission(interactions.Permissions.MANAGE_MESSAGES):
            if message_reaction.emoji.name == END_POLL_EMOJI:
                await self.close_poll(message_reaction.message)
                del POLLS[poll_id]
                await log_message(self, f"Poll `{poll.title}` has been closed by {message_reaction.author.mention}!")
        await message_reaction.message.remove_reaction(message_reaction.emoji, message_reaction.author)

def setup(client):
    PollSystem(client)
