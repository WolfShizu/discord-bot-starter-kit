import discord

from app.message_handler import MessageHandler

class DiscordClient(discord.Client):
    def __init__(self, message_handler: MessageHandler):
        self.message_handler = message_handler

        # Configura os privilégios do bot e o que ele receberá
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True

        super().__init__(intents=intents)
    
    # <---- Primeiro evento de conexão ---->
    async def on_ready(self) -> None:
        ...

    # <---- Eventos de Mensagens ---->
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await self.message_handler.handle_message(message)

    
    async def on_message_edit(self, message):
        ...
    
    async def on_message_delete(self, message):
        ...

    async def on_raw_message_delete(self, message):
        """Para mensagens antigas que não estão no cache do bot"""
        ...
    
    # <---- Eventos de Conexão ---->
    async def on_connect(self):
        """Chamado quando o bot se conecta, seja na primeira conexão ou após uma queda"""
        ...

    async def on_disconnect(self):
        """Chamado quando o bot se desconecta"""
        ...

    async def on_resumed(self):
        """Quando o bot se desconecta, mas retorna a conexão rapidamente, sem perder o cache"""
        ...
    
    # <---- Eventos de Membros e Servidores ---->
    async def on_member_join(self, member):
        ...
    
    async def on_member_remove(self, member):
        """Quando um usuário saiu ou foi expulso"""
        ...

    async def on_member_update(self, before, after):
        """Mudança de cargo, apelido ou status"""
        ...
    
    async def on_guild_join(self, guild):
        """O bot foi adicionado em um servidor"""
        ...

    # <---- Eventos de Reação e Interação ---->
    async def on_reaction_add(self, reaction, user):
        ...
    
    async def on_interaction(self, interaction):
        """Alguém usou slash command ou um botão"""
        ...
        