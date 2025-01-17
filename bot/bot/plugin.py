from mcdreforged.api.types import PluginServerInterface

from bot.constants import CONFIG_FILE_NAME
from bot.config import Config
from bot.bot_manager import BotManager
from bot.command_handler import CommandHandler
from bot.event_handler import EventHandler
from bot.location import Location

try:
    from bot.fastapi_manager import FastAPIManager
except ImportError:
    FastAPIManager = None


class Plugin:
    def __init__(self, server: PluginServerInterface, prev_module):
        self.__server = server
        self.__minecraft_data_api = self.__server.get_plugin_instance(
            'minecraft_data_api'
        )
        self.__config = self.__server.load_config_simple(
            CONFIG_FILE_NAME,
            target_class=Config
        )
        self.__check_config()

        self.__bot_manager = BotManager(self, prev_module)
        self.__fastapi_manager = None
        self.load_fastapi_manager()
        self.__command_handler = CommandHandler(self)
        self.__event_handler = EventHandler(self)

    def load_fastapi_manager(self):
        if FastAPIManager is not None:
            self.__fastapi_manager = FastAPIManager(self)
        else:
            self.server.logger.debug(
                "FastAPI library is not installed, "
                "will not register APIs with FastAPI MCDR."
            )

    def unload_fastapi_manager(self):
        if self.__fastapi_manager is not None:
            self.__fastapi_manager.unload()

    @property
    def fastapi_mcdr(self):
        return self.__server.get_plugin_instance('fastapi_mcdr')

    @property
    def server(self):
        return self.__server

    @property
    def minecraft_data_api(self):
        return self.__minecraft_data_api

    @property
    def config(self):
        return self.__config

    @property
    def bot_manager(self):
        return self.__bot_manager

    @property
    def fastapi_manager(self):
        return self.__fastapi_manager

    @property
    def command_handler(self):
        return self.__command_handler

    def __check_config(self):
        # flag
        save_flag = False

        # permission
        for name, level in Config.permissions.items():
            if name not in self.__config.permissions:
                self.server.logger.warning(
                    'During checking config, '
                    'permission "{}" not found, '
                    'will add it to config.'.format(name)
                )
                self.__config.permissions[name] = level
                save_flag = True

        # save
        if save_flag:
            self.server.save_config_simple(self.__config, CONFIG_FILE_NAME)

    def get_location(self, name: str) -> Location:
        """
        Get location from a player or bot.
        :param name: Name of player or bot.
        :return: A Location.
        """
        api = self.minecraft_data_api
        info = api.get_player_info(name)
        dimension = api.get_player_dimension(name)
        return Location(info['Pos'], info['Rotation'], dimension)
