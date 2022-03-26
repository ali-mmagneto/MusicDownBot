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
    'MusicDownBot',
    bot_token = Config.BOT_TOKEN,
    api_id = Config.API_ID,
    api_hash = Config.API_HASH
)


@bot.on_message(filters.command('start'))
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
    


@bot.on_message(filters.command('help'))
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

@bot.on_message(filters.command('ban'))
def ban(client, message):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(tld(chat.id, "You don't seem to be referring to a user."))
        return ""

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text(tld(chat.id, "I can't seem to find this user"))
            return ""
        else:
            raise

    if user_id == bot.id:
        message.reply_text(tld(chat.id, "I'm not gonna BAN myself, are you crazy?"))
        return ""

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text(tld(chat.id, "Why would I ban an admin? That sounds like a pretty dumb idea."))
        return ""

    log = "<b>{}:</b>" \
          "\n#BANNED" \
          "\n<b>• Admin:</b> {}" \
          "\n<b>• User:</b> {}" \
          "\n<b>• ID:</b> <code>{}</code>".format(html.escape(chat.title), mention_html(user.id, user.first_name), 
                                                  mention_html(member.user.id, member.user.first_name), user_id)

    reply = "{} has been banned!".format(mention_html(member.user.id, member.user.first_name))

    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        #bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        message.reply_text(tld(chat.id, "Banned!"))
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            #bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
            message.reply_text(tld(chat.id, "Banned!"), quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception("ERROR banning user %s in chat %s (%s) due to %s", user_id, chat.title, chat.id,
                             excp.message)
            message.reply_text(tld(chat.id, "Well damn, I can't ban that user."))

@bot.on_message(filters.command("buradamisin") & filters.user(Config.SUDO))
async def live(client: Client, message: Message):
    livemsg = await message.reply_text('`Canlıyım`')
    

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
        message.reply_audio(audio_file, caption=rep, parse_mode='md',quote=False, title=title, duration=dur, thumb=thumb_name, performer="@MusicDownBot")
        m.delete()
        bot.send_audio(chat_id=Config.PLAYLIST_ID, audio=audio_file, caption=rep, performer="@MusicDownBot", parse_mode='md', title=title, duration=dur, thumb=thumb_name)
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
