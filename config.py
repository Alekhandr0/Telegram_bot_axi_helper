import environ

def get_env():
    env = environ.Env()
    environ.Env.read_env()
    return {
        "telegram_bot_token": env('TELEGRAM_BOT_TOKEN'),
        "giga_auth_llm": env('AUTH_LLM'),
        "giga_auth_embed": env('AUTH_EMBED')
    }