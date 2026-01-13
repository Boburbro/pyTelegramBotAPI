from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS", default=[])
LANG_CODE = env.str("LANG_CODE", default="uz")
ip = env.str("ip", default=None)
