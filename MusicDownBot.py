import os, youtube_dl, requests, time
from config import Config
from youtube_search import YoutubeSearch
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message
)


bot = Client(
    'DemonBot',
    bot_token = Config.BOT_TOKEN,
    api_id = Config.API_ID,
    api_hash = Config.API_HASH
)


@app.on_message(filters.command('start'))
def start(client, message):
        message.reply_text(
        text="Merhabalar \nBen Benden istediğin müzikleri Youtube aracılığıyla sana getiren bir botum.", 
        quote=False,
        reply_markup=InlineKeyboardMarkup(
            [[
                    InlineKeyboardButton('Kişisel Blog', url='https://t.me/mmagneto3')
                  ],[
                    InlineKeyboardButton('Bot Sahibi', url=f'https://t.me/mmagneto')
                ]
            ]
        )
    )
    

@app.on_message(filters.command('help'))
def help(client, message):
    message.reply_text(
        text="**Help Mesajı** \n`/music` komutu ile benden müzik isteyebilirsin. \nÖrnek: \n `/music bones` /n ayrıca müzik ismi yerine youtube linkide kullanabilirsin.", 
        quote=False,
        reply_markup=InlineKeyboardMarkup(
            [[
                    InlineKeyboardButton('Kişisel Blog', url='https://t.me/mmagneto3')
                  ],[
                    InlineKeyboardButton('Bot Sahibi', url=f'https://t.me/mmagneto')
                ]
            ]
        )
    )

#alive mesaji#

@bot.on_message(filters.command("alive") & filters.user(Config.BOT_OWNER))
async def live(client: Client, message: Message):
    livemsg = await message.reply_text('`Mükəmməl İşləyirəm 😎`')
    
#musiqi əmri#

@bot.on_message(filters.command('music'))
def a(client, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('`Arıyom...`')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count>0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]
            views = results[0]["views"]
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            m.edit('Bu müziği bulamadım')
            return
    except Exception as e:
        m.edit(
            "Bu müziği bulamadım😔"
        )
        print(str(e))
        return
    m.edit("`Müziği buldum indiriyom.`")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"İndirildi [İndiren Bot](https://t.me/MusicDownBot)"
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode='md',quote=False, title=title, duration=dur, thumb=thumb_name, performer="@Botsinator")
        m.delete()
        bot.send_audio(chat_id=Config.PLAYLIST_ID, audio=audio_file, caption=rep, performer="@Botsinator", parse_mode='md', title=title, duration=dur, thumb=thumb_name)
    except Exception as e:
        m.edit('**Başaramadık abi**')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))

bot.run()
