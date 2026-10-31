import asyncio

import discord
import pyttsx3
import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


def speak(text):
    engine = pyttsx3.init()
    for voice in engine.getProperty("voices"):
        if "brazil" in voice.name.lower() or "pt-br" in voice.id.lower():
            engine.setProperty("voice", voice.id)
            break
    engine.say(text)
    engine.runAndWait()


def get_fact():
    for _ in range(3):
        try:
            r = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=15)
            if r.status_code == 200:
                text = r.json()["text"]
                try:
                    return GoogleTranslator(source="en", target="pt").translate(text)
                except Exception:
                    try:
                        return MyMemoryTranslator(source="en-US", target="pt-BR").translate(text)
                    except Exception:
                        return text
        except requests.RequestException:
            pass
    return "A API de curiosidades está fora do ar agora. Tente novamente em alguns minutos."


@bot.command()
async def start(ctx):
    await ctx.send(f"Olá, {ctx.author.mention}! Bem-vindo ao servidor!")


@bot.command()
async def fact(ctx):
    text = await asyncio.to_thread(get_fact)
    await ctx.send(f"Um fato interessante: {text}")
    await asyncio.to_thread(speak, text)

bot.run("seu token")