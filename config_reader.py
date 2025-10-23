from pydantic import SecretStr, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: SecretStr
    model_config = ConfigDict(env_file='GuessTheNumber/.env', env_file_encoding='utf-8')
    
config = Settings()
print(config.bot_token.get_secret_value())
