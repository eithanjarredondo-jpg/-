# =======================================================
#  𝐆𝐇𝐕𝐄𝐘𝐑𝐎𝐗 - Bot completo (Bienvenida + Verif + Tickets + Precios)
#  made by eithan.1
# =======================================================

import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

import config

load_dotenv()

# =======================================================
#  CONFIGURACIÓN
# =======================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =======================================================
#  FUNCIONES AUXILIARES
# =======================================================
def buscar_canal(guild, nombre):
    for canal in guild.text_channels:
        if canal.name.lower() == nombre.lower():
            return canal
    return None

def buscar_rol(guild, nombre):
    for rol in guild.roles:
        if rol.name.lower() == nombre.lower():
            return rol
    return None

def buscar_categoria(guild, nombre):
    for cat in guild.categories:
        if cat.name.lower() == nombre.lower():
            return cat
    return None

# =======================================================
#  EVENTO: BOT LISTO
# =======================================================
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"📊 Servidores: {len(bot.guilds)}")
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos sincronizados")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{config.NOMBRE_BOT} | Tickets"
        )
    )

# =======================================================
#  EVENTO: BIENVENIDA
# =======================================================
@bot.event
async def on_member_join(member):
    canal = buscar_canal(member.guild, config.NOMBRE_CANAL_BIENVENIDA)
    if not canal:
        return
    
    embed = discord.Embed(
        title=f"👋 ¡Bienvenido a {member.guild.name}!",
        description=(
            f"¡Hola {member.mention}! Nos alegra tenerte aquí.\n\n"
            f"📌 **Pasos a seguir:**\n"
            f"1️⃣ Ve al canal de verificación\n"
            f"2️⃣ Presiona el botón de verificación\n"
            f"3️⃣ ¡Accede a todo el servidor!"
        ),
        color=config.COLOR_PRINCIPAL
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.add_field(name="📅 Cuenta creada", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="👥 Miembro #", value=member.guild.member_count, inline=True)
    embed.set_footer(text=f"{member.guild.name} · ID: {member.id}")
    
    if config.URL_BANNER_BIENVENIDA:
        embed.set_image(url=config.URL_BANNER_BIENVENIDA)
    
    await canal.send(embed=embed)

# =======================================================
#  COMANDO: /testbienvenida
# =======================================================
@bot.tree.command(name="testbienvenida", description="Simula una bienvenida")
@app_commands.default_permissions(administrator=True)
async def testbienvenida(interaction: discord.Interaction):
    await on_member_join(interaction.user)
    await interaction.response.send_message("✅ Bienvenida simulada", ephemeral=True)

# =======================================================
#  COMANDO: /verificacion
# =======================================================
@bot.tree.command(name="verificacion", description="Envía el panel de verificación")
@app_commands.default_permissions(administrator=True)
async def verificacion(interaction: discord.Interaction):
    canal = buscar_canal(interaction.guild, config.NOMBRE_CANAL_VERIFICACION)
    
    if not canal:
        await interaction.response.send_message(
            f"❌ No encontré el canal **`{config.NOMBRE_CANAL_VERIFICACION}`**.",
            ephemeral=True
        )
        return
    
    embed = discord.Embed(
        title=f"BIENVENIDO/A A {config.NOMBRE_BOT}",
        description=(
            "**VERIFICACIÓN**\n\n"
            "Pulsa el botón para verificar tu cuenta."
        ),
        color=config.COLOR_PRINCIPAL
    )
    
    if config.URL_BANNER_VERIFICACION:
        embed.set_image(url=config.URL_BANNER_VERIFICACION)
    
    embed.set_footer(text=f"{config.NOMBRE_BOT} · Sistema de Verificación")
    
    view = VerificacionView()
    await canal.send(embed=embed, view=view)
    await interaction.response.send_message(f"✅ Panel enviado a {canal.mention}", ephemeral=True)

# =======================================================
#  VISTA: VERIFICACIÓN
# =======================================================
class VerificacionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Verificarme", emoji="✅", style=discord.ButtonStyle.success, custom_id="ghveyrox_verificar")
    async def verificar(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        miembro = guild.get_member(interaction.user.id)
        
        rol_verificado = buscar_rol(guild, config.NOMBRE_ROL_VERIFICADO)
        
        if not rol_verificado:
            await interaction.response.send_message(f"❌ No encontré el rol **`{config.NOMBRE_ROL_VERIFICADO}`**.", ephemeral=True)
            return
        
        if rol_verificado in miembro.roles:
            await interaction.response.send_message("✅ Ya estás verificado.", ephemeral=True)
            return
        
        try:
            await miembro.add_roles(rol_verificado, reason="Verificación")
            
            rol_no_verif = buscar_rol(guild, config.NOMBRE_ROL_NO_VERIFICADO)
            if rol_no_verif and rol_no_verif in miembro.roles:
                await miembro.remove_roles(rol_no_verif)
            
            embed = discord.Embed(title="✅ ¡Verificado!", description=f"¡Felicidades {interaction.user.mention}!\n\nYa tienes acceso al servidor.", color=config.COLOR_EXITO)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.response.send_message("❌ No tengo permiso para darte el rol.", ephemeral=True)

# =======================================================
#  COMANDO: /tickets
# =======================================================
@bot.tree.command(name="tickets", description="Envía el panel de tickets")
@app_commands.default_permissions(administrator=True)
async def tickets(interaction: discord.Interaction):
    canal = buscar_canal(interaction.guild, config.NOMBRE_CANAL_TICKETS)
    
    if not canal:
        await interaction.response.send_message(f"❌ No encontré el canal **`{config.NOMBRE_CANAL_TICKETS}`**.", ephemeral=True)
        return
    
    # Generar descripción de categorías
    desc = "**Abre el ticket correcto para que el equipo pueda atenderte.**\n\n**📋 Categorías**\n\n"
    for opcion in config.TICKETS_OPCIONES:
        desc += f"{opcion['emoji']} **{opcion['label']}** · {opcion['description']}\n"
    
    embed = discord.Embed(title=f"🎫 Soporte · {config.NOMBRE_BOT}", description=desc, color=config.COLOR_TICKET)
    embed.set_footer(text=f"{config.NOMBRE_BOT} · Selecciona una categoría abajo")
    
    view = TicketsView()
    await canal.send(embed=embed, view=view)
    await interaction.response.send_message(f"✅ Panel enviado a {canal.mention}", ephemeral=True)

# =======================================================
#  VISTA: TICKETS
# =======================================================
class TicketsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketsSelect())

class TicketsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=op["label"], emoji=op["emoji"], description=op["description"])
            for op in config.TICKETS_OPCIONES
        ]
        super().__init__(placeholder="Selecciona una categoría...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        categoria = self.values[0]
        guild = interaction.guild
        user = interaction.user
        
        for channel in guild.channels:
            if channel.name == f"ticket-{user.name.lower()}":
                await interaction.response.send_message(f"❌ Ya tienes un ticket: {channel.mention}", ephemeral=True)
                return
        
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
            
            rol_staff = buscar_rol(guild, config.NOMBRE_ROL_STAFF)
            if rol_staff:
                overwrites[rol_staff] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            categoria_discord = buscar_categoria(guild, config.NOMBRE_CATEGORIA_TICKETS)
            
            canal = await guild.create_text_channel(
                name=f"ticket-{user.name.lower()}",
                category=categoria_discord,
                overwrites=overwrites,
                topic=f"Ticket de {user.name} · {categoria}"
            )
            
            embed = discord.Embed(title=f"🎫 Ticket · {categoria}", description=f"Hola {user.mention}, un miembro del equipo te atenderá pronto.\n\n**Categoría:** {categoria}", color=config.COLOR_TICKET)
            embed.set_footer(text=f"{config.NOMBRE_BOT} · Cierra con el botón")
            
            await canal.send(embed=embed, view=CerrarTicketView(user))
            await interaction.response.send_message(f"✅ Ticket creado: {canal.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

# =======================================================
#  VISTA: CERRAR TICKET
# =======================================================
class CerrarTicketView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user
    
    @discord.ui.button(label="Cerrar Ticket", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="ghveyrox_cerrar")
    async def cerrar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Solo el creador o un admin puede cerrar el ticket.", ephemeral=True)
            return
        
        await interaction.response.send_message("🔒 Cerrando ticket en 5 segundos...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# =======================================================
#  COMANDO: /precios
# =======================================================
@bot.tree.command(name="precios", description="Muestra los precios")
@app_commands.default_permissions(administrator=True)
async def precios(interaction: discord.Interaction):
    canal = buscar_canal(interaction.guild, config.NOMBRE_CANAL_PRECIOS)
    
    if not canal:
        await interaction.response.send_message(f"❌ No encontré el canal **`{config.NOMBRE_CANAL_PRECIOS}`**.", ephemeral=True)
        return
    
    embed = discord.Embed(title=f"💰 PRECIOS · {config.NOMBRE_BOT}", description="Precios profesionales de intros", color=config.COLOR_PRECIO)
    
    for p in config.PRECIOS:
        embed.add_field(name=f"{p['emoji']} {p['nombre']} · **{p['precio']}**", value=f"```{p['detalles']}```", inline=False)
    
    embed.set_footer(text=f"{config.NOMBRE_BOT} · Precios actualizados")
    
    await canal.send(embed=embed)
    await interaction.response.send_message(f"✅ Precios enviados a {canal.mention}", ephemeral=True)

# =======================================================
#  EJECUCIÓN
# =======================================================
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERROR: No se encontró DISCORD_TOKEN")
    else:
        print(f"🚀 Iniciando {config.NOMBRE_BOT}...")
        bot.run(TOKEN)