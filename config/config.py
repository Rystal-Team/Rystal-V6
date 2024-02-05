from nextcord import Color

"""
=== EMBEDs COLORS === 
"""
type_color = {
    "success": Color.from_rgb(157, 255, 158),
    "error": Color.from_rgb(255, 157, 157),
    "warn": Color.from_rgb(255, 206, 157),
    "info": Color.from_rgb(219, 157, 255),
    "list": Color.from_rgb(157, 200, 255),
}

"""
=== EMBEDs TITLE ===
"""
music_class_title = "🎵 | Music Module"
level_class_title = "🎵 | Leveling Module"

"""
=== ADMINISTRATION === 
"""
# the channel id for error logging
error_log_channel_id = 1203877839917555722
# the user id of the owner of bot, or the person you want to have admin access to the bot
bot_owner_id = 699452241312219147

"""
=== ACTIVITY LOGGING === 
I do not recommend turning this on as it does slow down the bot quite a bit
if you are running it on a low end server/computer, however if you really really 
want to then go ahead, the error logging should be more than enough though.!!!
"""
# whether you want activity logging or not, defaults to False
enable_activity_logging = False
# the channel id for logging (only required if activity logging is enabled, type None or "" if you don't need it)
logging_channe_id = 1203866958487879680


