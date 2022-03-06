import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from bot import app
from sys import executable

from telegram import ParseMode
from telegram.ext import CommandHandler
from wserver import start_server_async
from bot import bot, IMAGE_URL, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, SERVER_PORT
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, torrent_search, delete, speedtest, count, config, updates


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>╭──「⭕️ BOT STATISTICS ⭕️」</b>\n' \
            f'<b>│</b>\n' \
            f'<b>├  ⏰ Bot Uptime : {currentTime}</b>\n' \
            f'<b>├  💾 Total Disk Space : {total}</b>\n' \
            f'<b>├  📀 Total Used Space : {used}</b>\n' \
            f'<b>├  💿 Total Free Space : {free}</b>\n' \
            f'<b>├  🔼 Total Upload : {sent}</b>\n' \
            f'<b>├  🔽 Total Download : {recv}</b>\n' \
            f'<b>├  🖥️ CPU : {cpuUsage}%</b>\n' \
            f'<b>├  🎮 RAM : {memory}%</b>\n' \
            f'<b>├  💽 DISK : {disk}%</b>\n' \
            f'<b>│</b>\n' \
            f'<b>╰──「 🚸 @kang_salin 🚸 」</b>'
    update.effective_message.reply_photo(IMAGE_URL, stats, parse_mode=ParseMode.HTML)


def start(update, context):
    start_string = f'''
Bot ini dapat mencerminkan semua tautan Anda ke Google Drive!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Repo", "https://github.com/ayushteke/slam_aria_mirror_bot")
    buttons.buildbutton("Channel", "https://t.me/AT_BOTs")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    LOGGER.info('UID: {} - UN: {} - MSG: {}'.format(update.message.chat.id, update.message.chat.username, update.message.text))
    uptime = get_readable_time((time.time() - botStartTime))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        if update.message.chat.type == "private" :
            sendMessage(f"Hey I'm Alive 🙂\nSince: <code>{uptime}</code>", context.bot, update)
        else :
            sendMarkup(IMAGE_URL, start_string, context.bot, update, reply_markup)
    else :
        sendMarkup(f"Oops! You are not allowed to use me.</b>.", context.bot, update, reply_markup)


def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f'''
/{BotCommands.HelpCommand}: Untuk mendapatkan pesan ini
/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai mirroring tautan ke Google Drive. Menggunakan /{BotCommands.MirrorCommand} qb untuk mencerminkan dengan qBittorrent, dan gunakan /{BotCommands.MirrorCommand} qbs untuk memilih file sebelum mengunduh
/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah versi unduhan (.tar) yang diarsipkan
/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah versi unduhan (.zip) yang diarsipkan
/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan jika file yang diunduh adalah arsip apa pun, ekstrak ke Google Drive
/{BotCommands.CloneCommand} [drive_url]: Salin file/folder ke Google Drive
/{BotCommands.CountCommand} [drive_url]: Hitung file/folder dari Google Drive Links
/{BotCommands.DeleteCommand} [drive_url]: Hapus file dari Google Drive (Hanya Pemilik & Sudo)
/{BotCommands.WatchCommand} [youtube-dl supported link]: Cermin melalui youtube-dl. Klik /{BotCommands.WatchCommand} untuk bantuan lebih lanjut
/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror melalui youtube-dl dan tar sebelum mengunggah
/{BotCommands.CancelMirror}: Balas pesan yang digunakan untuk mengunduh dan unduhan itu akan dibatalkan
/{BotCommands.CancelAllCommand}: Batalkan semua tugas yang sedang berjalan
/{BotCommands.ListCommand} [search term]: Mencari istilah pencarian di Google Drive, Jika ditemukan balasan dengan tautan
/{BotCommands.StatusCommand}: Menunjukkan status semua unduhan
/{BotCommands.StatsCommand}: Tampilkan Statistik mesin tempat bot dihosting
/{BotCommands.PingCommand}: Periksa berapa lama waktu yang dibutuhkan untuk melakukan Ping Bot
/{BotCommands.AuthorizeCommand}: Otorisasi obrolan atau pengguna untuk menggunakan bot (Hanya dapat dipanggil oleh Pemilik & Sudo bot)
/{BotCommands.UnAuthorizeCommand}: Batalkan otorisasi obrolan atau pengguna untuk menggunakan bot (Hanya dapat dipanggil oleh Pemilik & Sudo bot)
/{BotCommands.AuthorizedUsersCommand}: Tampilkan pengguna resmi (Hanya Pemilik & Sudo)
/{BotCommands.AddSudoCommand}: Tambahkan pengguna Sudo (Hanya Pemilik)
/{BotCommands.RmSudoCommand}: Hapus pengguna Sudo (Hanya Pemilik)
/{BotCommands.RestartCommand}: Mulai ulang bot
/{BotCommands.LogCommand}: Dapatkan file log bot. Berguna untuk mendapatkan laporan kerusakan
/{BotCommands.ConfigMenuCommand}: Dapatkan Menu Info tentang konfigurasi bot (Hanya Pemilik)
/{BotCommands.UpdateCommand}: Perbarui Bot dari Repo Hulu (Khusus Pemilik)
/{BotCommands.SpeedCommand}: Periksa Kecepatan Internet Tuan Rumah
/{BotCommands.ShellCommand}: Jalankan perintah di Shell (Terminal)
/{BotCommands.ExecHelpCommand}: Dapatkan bantuan untuk modul Pelaksana (Hanya Pemilik)
/{BotCommands.TsHelpCommand}: Dapatkan bantuan untuk modul pencarian Torrent
'''

    help_string = f'''
/{BotCommands.MirrorCommand} [download_url][magnet_link]: Mulai mirroring tautan ke Google Drive. Menggunakan /{BotCommands.MirrorCommand} qb untuk mencerminkan dengan qBittorrent, dan gunakan /{BotCommands.MirrorCommand} qbs untuk memilih file sebelum mengunduh
/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah versi unduhan (.tar) yang diarsipkan
/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan unggah versi unduhan (.zip) yang diarsipkan
/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Mulai mirroring dan jika file yang diunduh adalah arsip apa pun, ekstrak ke Google Drive
/{BotCommands.CloneCommand} [drive_url]: Salin file/folder ke Google Drive
/{BotCommands.CountCommand} [drive_url]: Hitung file/folder dari Google Drive Links
/{BotCommands.WatchCommand} [youtube-dl supported link]: Cermin melalui youtube-dl. Klik /{BotCommands.WatchCommand} untuk bantuan lebih lanjut
/{BotCommands.TarWatchCommand} [youtube-dl supported link]: Mirror melalui youtube-dl dan tar sebelum mengunggah
/{BotCommands.CancelMirror}: Balas pesan yang digunakan untuk mengunduh dan unduhan itu akan dibatalkan
/{BotCommands.ListCommand} [search term]: Mencari istilah pencarian di Google Drive, Jika ditemukan balasan dengan tautan
/{BotCommands.StatusCommand}: Menunjukkan status semua unduhan
/{BotCommands.StatsCommand}: Tampilkan Statistik mesin tempat bot dihosting
/{BotCommands.PingCommand}: Periksa berapa lama waktu yang dibutuhkan untuk melakukan Ping Bot
/{BotCommands.TsHelpCommand}: Dapatkan bantuan untuk modul pencarian Torrent
'''

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


botcmds = [
        (f'{BotCommands.HelpCommand}','Dapatkan Bantuan Mendetail'),
        (f'{BotCommands.MirrorCommand}', 'Mulai Unduh'),
        (f'{BotCommands.TarMirrorCommand}','Mulai Unduh dan unggah sebagai .tar'),
        (f'{BotCommands.UnzipMirrorCommand}','Ekstrak file'),
        (f'{BotCommands.ZipMirrorCommand}','Mulai Unduh dan unggah sebagai .zip'),
        (f'{BotCommands.CloneCommand}','Salin file/folder ke Drive'),
        (f'{BotCommands.CountCommand}','Hitung file/folder tautan Drive'),
        (f'{BotCommands.DeleteCommand}','Hapus file dari Drive'),
        (f'{BotCommands.WatchCommand}','Tautan dukungan Mirror Youtube-dl'),
        (f'{BotCommands.TarWatchCommand}','Unduh tautan daftar putar Youtube sebagai .tar'),
        (f'{BotCommands.CancelMirror}','Membatalkan tugas'),
        (f'{BotCommands.CancelAllCommand}','Batalkan semua tugas'),
        (f'{BotCommands.ListCommand}','Mencari file di Drive'),
        (f'{BotCommands.StatusCommand}','Dapatkan pesan Status Cermin'),
        (f'{BotCommands.StatsCommand}','Statistik Penggunaan Bot'),
        (f'{BotCommands.PingCommand}','Ping Bot'),
        (f'{BotCommands.RestartCommand}','Mulai ulang bot [pemilik/sudo saja]'),
        (f'{BotCommands.LogCommand}','Dapatkan Bot Log [pemilik/sudo saja]'),
        (f'{BotCommands.TsHelpCommand}','Dapatkan bantuan untuk modul pencarian Torrent')
    ]


def main():
    fs_utils.start_cleanup()

    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(SERVER_PORT))

    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
