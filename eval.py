import discord, asyncio, aiohttp, os, sys, time, datetime, random, requests, aeval # Импорты библиотек
from discord.ext import commands, tasks # Импорты дополнений (extensions) из d.py

bot = commands.Bot(command_prefix = commands.when_mentioned_or('!'), intents = discord.Intents.all())
# Пояснение: тут префикс - это либо упоминание бота, либо "!"; intents - "нмерения доступа к шлюзам API", они нужны для получения некоторых данных (я выбрал все, но можете посмотреть в документации)

def minify_text(txt):
    if len(txt) >= 1024:
        return f'''{str(txt)[:-900]}...
        # ...и ещё {len(str(txt).replace(str(txt)[:-900], ""))} символов...'''
    else:
        return str(txt) # Захотелось использовать лямбду и всё в одну строку... но решил хоть как-то сделать читабельней

@bot.command(aliases = ['eval', 'aeval', 'evaulate', 'выполнить', 'exec', 'execute'])
async def __eval(ctx, *, content):
    if ctx.author.id not in bot.owner_ids: return await ctx.send("Кыш!") # Защита от os.system('format C') :)
    # Проверка на то, записан ли код в Markdown'овском блоке кода и его "очистка":
    code = "\n".join(content.split("\n")[1:])[:-3] if content.startswith("```") and content.endswith("```") else content
    standart_args = { # Стандартные библиотеки и переменные, которые будут определены в коде. Для удобства. Кстати, я уже добавил несколько встроенных либ и переменных из d.py
        "discord": discord,
        "commands": commands,
        "bot": bot,
        "tasks": tasks,
        "ctx": ctx,
        "asyncio": asyncio,
        "aiohttp": aiohttp,
        "os": os,
        'sys': sys,
        "time": time,
        "datetime": datetime,
        "random": random,
        "requests": requests
    }
    start = time.time() # запись стартового таймстампа для расчёта времени выполнения
    try:
        r = await aeval.aeval(f"""{code}""", standart_args, {}) # выполняем код
        ended = time.time() - start # рассчитываем конец выполнения
        print(r)
        if not code.startswith('#nooutput'): # Если код начинается с #nooutput, то вывода не будет
            embed = discord.Embed(title = "Успешно!", description = f"Выполнено за: {ended}", color = 0x99ff99)
            """
             Есть нюанс: если входные/выходные данные будут длиннее 1024 символов, то эмбед не отправится, а функция выдаст ошибку.
             Именно поэтому сверху стоит print(r), а так же есть функция minify_text, которая
             минифицирует текст для эмбеда во избежание БэдРеквеста (который тут возникает когда слишком много символов). Поставил специально лимит на 900, чтобы точно хватило
            """
            embed.add_field(name = f'Входные данные:', value = f'`{minify_text(code) }`')
            embed.add_field(name = f'Выходные данные:', value = f'`{minify_text(r) }`', inline=False) 
            await ctx.send(embed = embed) # Отправка, уиии
    except Exception as e: # Ловим ошибки из строки с выполнением нашего кода (и не только!)
        ended = time.time() - start # Сново считаем время, но на этот раз до ошибки
        if not code.startswith('#nooutput'): # Аналогично коду выше
            code = minify_text(code)
            embed = discord.Embed(title = f"При выполнении возникла ошибка.\nВремя: {ended}", description = f'Ошибка:\n```py\n{e}```', color = 0xff0000)
            embed.add_field(name = f'Входные данные:', value = f'`{minify_text(code)}`', inline=False)
            await ctx.send(embed = embed)
            raise e # Ну и поднимем исключение
bot.run('Токен бота из приложения на "discord.com/developers/applications". P. S. Не забудьте включить два параметра после заголовка Priveleged Gateway Intents')
