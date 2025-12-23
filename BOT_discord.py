import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration des rôles pour chaque message
ROLES_GENRE = {
    '👨': 'Homme',
    '👩': 'Femme',
    '🌈': 'Non-binaire'
}

ROLES_JEUX = {
    '🎯': 'Valorant',
    '🏗️': 'Fortnite',
    '⛏️': 'Minecraft',
    '⚽': 'Rocket League',
    '🔫': 'Call of Duty',
    '🗡️': 'League of Legends'
}

ROLES_PLATEFORME = {
    '💻': 'PC',
    '🎮': 'PlayStation',
    '📱': 'Téléphone',
    '❎': 'Xbox'
}

# Configuration pour les messages d'au revoir
SALON_AU_REVOIR_ID = None  # À configurer avec !set_aurevoir

# Dictionnaire qui regroupe tout
ALL_ROLES = {}
ALL_ROLES.update(ROLES_GENRE)
ALL_ROLES.update(ROLES_JEUX)
ALL_ROLES.update(ROLES_PLATEFORME)

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté!')
    print('Bot prêt à fonctionner')

@bot.command(name='setup_roles')
@commands.has_permissions(administrator=True)
async def setup_roles(ctx):
    """Crée les 3 messages de sélection des rôles"""
    
    # ID du salon "roles"
    SALON_ROLES_ID = 1452831961960677499
    
    # Récupérer le salon
    salon_roles = bot.get_channel(SALON_ROLES_ID)
    
    if salon_roles is None:
        await ctx.send("❌ Je ne trouve pas le salon roles!")
        return
    
    # MESSAGE 1 : GENRE
    embed1 = discord.Embed(
        title="👤 Choisis ton genre",
        description="Réagis avec un emoji pour choisir ton genre !",
        color=discord.Color.purple()
    )
    
    roles_text1 = ""
    for emoji, role_name in ROLES_GENRE.items():
        roles_text1 += f"{emoji} - {role_name}\n"
    embed1.add_field(name="Genres disponibles:", value=roles_text1, inline=False)
    
    message1 = await salon_roles.send(embed=embed1)
    for emoji in ROLES_GENRE.keys():
        await message1.add_reaction(emoji)
    
    # MESSAGE 2 : JEUX
    embed2 = discord.Embed(
        title="🎮 Choisis tes jeux",
        description="Réagis avec les emojis des jeux auxquels tu joues !",
        color=discord.Color.green()
    )
    
    roles_text2 = ""
    for emoji, role_name in ROLES_JEUX.items():
        roles_text2 += f"{emoji} - {role_name}\n"
    embed2.add_field(name="Jeux disponibles:", value=roles_text2, inline=False)
    
    message2 = await salon_roles.send(embed=embed2)
    for emoji in ROLES_JEUX.keys():
        await message2.add_reaction(emoji)
    
    # MESSAGE 3 : PLATEFORMES
    embed3 = discord.Embed(
        title="🖥️ Choisis tes plateformes",
        description="Réagis avec les emojis des plateformes que tu utilises !",
        color=discord.Color.blue()
    )
    
    roles_text3 = ""
    for emoji, role_name in ROLES_PLATEFORME.items():
        roles_text3 += f"{emoji} - {role_name}\n"
    embed3.add_field(name="Plateformes disponibles:", value=roles_text3, inline=False)
    
    message3 = await salon_roles.send(embed=embed3)
    for emoji in ROLES_PLATEFORME.keys():
        await message3.add_reaction(emoji)
    
    await ctx.send("✅ Les 3 messages de rôles ont été créés dans le salon roles!")
    print("Les 3 messages de rôles ont été créés!")

@bot.event
async def on_raw_reaction_add(payload):
    """Quand quelqu'un ajoute une réaction"""
    
    # Ignorer les réactions du bot
    if payload.user_id == bot.user.id:
        return
    
    # Récupérer le serveur et le membre
    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return
    
    member = guild.get_member(payload.user_id)
    if member is None:
        return
    
    # Vérifier si l'emoji correspond à un rôle
    emoji = str(payload.emoji)
    if emoji in ALL_ROLES:
        role_name = ALL_ROLES[emoji]
        
        # Chercher le rôle
        role = discord.utils.get(guild.roles, name=role_name)
        
        if role is None:
            print(f"Le rôle {role_name} n'existe pas sur le serveur!")
            return
        
        # Donner le rôle
        try:
            await member.add_roles(role)
            print(f"{member.name} a reçu le rôle {role_name}")
        except Exception as e:
            print(f"Erreur: {e}")

@bot.event
async def on_raw_reaction_remove(payload):
    """Quand quelqu'un enlève une réaction"""
    
    # Récupérer le serveur et le membre
    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return
    
    member = guild.get_member(payload.user_id)
    if member is None:
        return
    
    # Vérifier si l'emoji correspond à un rôle
    emoji = str(payload.emoji)
    if emoji in ALL_ROLES:
        role_name = ALL_ROLES[emoji]
        
        # Chercher le rôle
        role = discord.utils.get(guild.roles, name=role_name)
        
        if role is None:
            return
        
        # Retirer le rôle
        try:
            await member.remove_roles(role)
            print(f"{member.name} a perdu le rôle {role_name}")
        except Exception as e:
            print(f"Erreur: {e}")

@bot.command(name='set_aurevoir')
@commands.has_permissions(administrator=True)
async def set_aurevoir(ctx, channel_id: int):
    """Configure le salon pour les messages d'au revoir"""
    global SALON_AU_REVOIR_ID
    
    # Vérifier que le salon existe
    channel = bot.get_channel(channel_id)
    if channel is None:
        await ctx.send("❌ Ce salon n'existe pas!")
        return
    
    SALON_AU_REVOIR_ID = channel_id
    await ctx.send(f"✅ Les messages d'au revoir seront envoyés dans {channel.mention}")

@bot.event
async def on_member_remove(member):
    """Quand quelqu'un quitte le serveur"""
    
    if SALON_AU_REVOIR_ID is None:
        return
    
    # Récupérer le salon
    salon = bot.get_channel(SALON_AU_REVOIR_ID)
    if salon is None:
        return
    
    # Messages d'au revoir aléatoires
    messages = [
        f"👋 **{member.name}** vient de quitter le serveur... Au revoir!",
        f"😢 **{member.name}** nous a quitté. On te souhaite bonne chance!",
        f"👋 C'est avec tristesse que nous disons au revoir à **{member.name}**",
        f"🚪 **{member.name}** a quitté le serveur. À bientôt peut-être!",
        f"😔 **{member.name}** est parti(e). Merci pour les moments passés ensemble!"
    ]
    
    # Choisir un message aléatoire
    import random
    message = random.choice(messages)
    
    # Créer un embed
    embed = discord.Embed(
        description=message,
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Le serveur compte maintenant {member.guild.member_count} membres")
    
    try:
        await salon.send(embed=embed)
        print(f"{member.name} a quitté le serveur")
    except Exception as e:
        print(f"Erreur lors de l'envoi du message d'au revoir: {e}")

# Lancer le bot
if __name__ == "__main__":
    TOKEN = os.getenv('TOKEN')
    if TOKEN is None:
        print("❌ ERREUR: Le token n'est pas configuré!")
        print("Ajoute la variable TOKEN dans les variables d'environnement de Railway")
    else:
        bot.run(TOKEN)
