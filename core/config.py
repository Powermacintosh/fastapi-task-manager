# -*- encoding: utf-8 -*-
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ConfigurationDB(BaseModel):
    #########################
    #  PostgreSQL database  #
    #########################
    load_dotenv()
    
    MODE: str = os.getenv('MODE')
    
    DB_USER: str = os.getenv('DB_USER')
    DB_PASS: str = os.getenv('DB_PASS')
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int = os.getenv('DB_PORT', 5432)
    DB_NAME: str = os.getenv('DB_NAME')
    
    @property
    def async_url(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    echo: bool = False


class ConfigurationCORS(BaseModel):
    #########################
    #         CORS          #
    #########################
    origins: list = ['*']
    allow_credentials: bool = True
    methods: list = [
        'GET',
        'POST',
        'OPTIONS',
        'PATCH',
        'PUT',
        'DELETE',
    ]
    headers: list = [
        'Access-Control-Allow-Headers',
        'Content-Type',
        'Set-Cookie',
        'Authorization',
        'Access-Control-Allow-Origin',
    ]

class ConfigurationLoki(BaseModel):
    #########################
    #         Loki          #
    #########################
    LOKI_PORT: int = os.getenv('LOKI_PORT')

    @property
    def url(self):
        return f'http://loki:{self.LOKI_PORT}/loki/api/v1/push'
    
class Setting(BaseSettings):
    # FASTAPI
    api_v1_prefix: str = '/api/v1'
    api_v1_port: int = os.getenv('APP_PORT')
    
    # LOKI
    loki: ConfigurationLoki = ConfigurationLoki()
    
    # DATABASE
    db: ConfigurationDB = ConfigurationDB()
    
    # CORS
    cors: ConfigurationCORS = ConfigurationCORS()
    

settings = Setting()