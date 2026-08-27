import random
from typing import Optional

import discord

from config import ERROR_COLOR, INVITE_URL, SUCCESS_COLOR
import content.pictures as pic
from utils.helpers import create_embed


class FortuneCardView(discord.ui.View):
    """Interactive card choice view for /fortuna command."""

    def __init__(
        self,
        author: discord.User | discord.Member,
        client_user: Optional[discord.ClientUser] = None
    ):
        super().__init__(timeout=45.0)
        self.author = author
        self.client_user = client_user
        self.winner_index = random.randint(0, 3)
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "Tylko osoba, która poprosiła Ranalda o pomoc, może wybrać kartę!",
                ephemeral=True
            )
            return False
        return True

    async def handle_card_choice(self, interaction: discord.Interaction, card_index: int):
        # Disable all buttons upon selection
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        if card_index == self.winner_index:
            win_card_url = pic.WIN_CARDS[card_index]
            embed = create_embed(
                title="🤞 Twój wybór...",
                description=f"Świetnie {self.author.mention}, dziś Ranald wysłuchał Twej prośby!",
                color=SUCCESS_COLOR,
                image_url=win_card_url,
                client_user=self.client_user
            )
        else:
            lose_card_url = pic.LOSE_CARDS[card_index]
            winning_card_number = self.winner_index + 1
            embed = create_embed(
                title="🤞 Twój wybór...",
                description=(
                    f"{self.author.mention}, to był bardzo zły wybór...\n\n"
                    f"Szczęśliwą kartą była **karta nr {winning_card_number}**."
                ),
                color=ERROR_COLOR,
                image_url=lose_card_url,
                client_user=self.client_user
            )

        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="", emoji="1️⃣", style=discord.ButtonStyle.secondary)
    async def card_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_card_choice(interaction, 0)

    @discord.ui.button(label="", emoji="2️⃣", style=discord.ButtonStyle.secondary)
    async def card_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_card_choice(interaction, 1)

    @discord.ui.button(label="", emoji="3️⃣", style=discord.ButtonStyle.secondary)
    async def card_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_card_choice(interaction, 2)

    @discord.ui.button(label="", emoji="4️⃣", style=discord.ButtonStyle.secondary)
    async def card_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_card_choice(interaction, 3)

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        if self.message:
            timeout_embed = create_embed(
                title="Za późno...",
                description=f"{self.author.mention}, Twój czas na wybór karty minął.",
                color=ERROR_COLOR,
                client_user=self.client_user
            )
            try:
                await self.message.edit(embed=timeout_embed, view=self)
            except discord.HTTPException:
                pass


class InviteView(discord.ui.View):
    """Button linking to the bot's invite authorization."""

    def __init__(self):
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="Zaproś bota na serwer",
                url=INVITE_URL,
                style=discord.ButtonStyle.link,
                emoji="🔗"
            )
        )
