import os
import discord
import asyncio
import functools
from collections import defaultdict
from core.json_io import JsonIO


GLOBAL_KEY = '__global__'
SENTINEL = object()


class JsonDB(JsonIO):
    """
    A DB-like helper class to streamline the saving of json files

    Parameters:

    file_path: str
        The path of the json file you want to create / access
    create_dirs: bool=False
        If True, it will create any missing directory leading to
        the file you want to create
    default_value: Optional=None
        Same behaviour as a defaultdict
    """

    def __init__(self, file_path, **kwargs):
        create_dirs = kwargs.pop("create_dirs", False)
        default_value = kwargs.pop("default_value", SENTINEL)
        self.autosave = kwargs.pop("autosave", False)
        self.path = file_path

        file_exists = os.path.isfile(file_path)

        if create_dirs and not file_exists:
            path, _ = os.path.split(file_path)
            if path:
                try:
                    os.makedirs(path)
                except FileExistsError:
                    pass

        if file_exists:
            # Might be worth looking into threadsafe ways for very large files
            self._data = self._load_json(file_path)
        else:
            self._data = {}
            self._blocking_save()

        if default_value is not SENTINEL:
            def _get_default():
                return default_value
            self._data = defaultdict(_get_default, self._data)

        self._loop = asyncio.get_event_loop()
        self._task = functools.partial(self._threadsafe_save_json, self._data)

    async def set(self, key, value):
        """Sets a DB's entry"""
        self._data[key] = value
        await self.save()

    def get(self, key, default=None):
        """Returns a DB's entry"""
        return self._data.get(key, default)

    async def remove(self, key):
        """Removes a DB's entry"""
        del self._data[key]
        await self.save()

    async def pop(self, key, default=None):
        """Removes and returns a DB's entry"""
        value = self._data.pop(key, default)
        await self.save()
        return value

    async def wipe(self):
        """Wipes DB"""
        self._data = {}
        await self.save()

    def all(self):
        """Returns all DB's data"""
        return self._data

    def _blocking_save(self):
        """Using this should be avoided. Let's stick to threadsafe saves"""
        self._save_json(self.path, self._data)

    async def save(self):
        """Threadsafe save to file"""
        await self._threadsafe_save_json(self.path, self._data)

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self._data)


class JsonGuildDB(JsonDB):
    """
    A DB-like helper class to streamline the saving of json files
    This is a variant of JsonDB that allows for guild specific data
    Global data is still allowed with dedicated methods

    Same parameters as JsonDB
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def set(self, guild, key, value):
        """Sets a guild's entry"""
        if not isinstance(guild, discord.Guild):
            raise TypeError('Can only set guild data')
        if str(guild.id) not in self._data:
            self._data[str(guild.id)] = {}
        self._data[str(guild.id)][key] = value
        await self.save()

    def get(self, guild, key, default=None):
        """Returns a guild's entry"""
        if not isinstance(guild, discord.Guild):
            raise TypeError('Can only get guild data')
        if str(guild.id) not in self._data:
            return default
        return self._data[str(guild.id)].get(key, default)

    async def remove(self, guild, key):
        """Removes a guild's entry"""
        if not isinstance(guild, discord.Guild):
            raise TypeError('Can only remove guild data')
        if str(guild.id) not in self._data:
            raise KeyError('Guild data is not present')
        del self._data[str(guild.id)][key]
        await self.save()

    async def pop(self, guild, key, default=None):
        """Removes and returns a guild's entry"""
        if not isinstance(guild, discord.Guild):
            raise TypeError('Can only remove guild data')
        value = self._data.get(str(guild.id), {}).pop(key, default)
        await self.save()
        return value

    def get_all(self, guild, default):
        """Returns all entries of a guild"""
        if not isinstance(guild, discord.Guild):
            raise TypeError('Can only get guild data')
        return self._data.get(str(guild.id), default)

    async def remove_all(self, guild):
        """Removes all entries of a guild"""
        if not isinstance(guild, discord.Guild):
            raise TypeError('Can only remove guilds')
        await super().remove(str(guild.id))

    async def set_global(self, key, value):
        """Sets a global value"""
        if GLOBAL_KEY not in self._data:
            self._data[GLOBAL_KEY] = {}
        self._data[GLOBAL_KEY][key] = value
        await self.save()

    def get_global(self, key, default=None):
        """Gets a global value"""
        if GLOBAL_KEY not in self._data:
            self._data[GLOBAL_KEY] = {}

        return self._data[GLOBAL_KEY].get(key, default)

    async def remove_global(self, key):
        """Removes a global value"""
        if GLOBAL_KEY not in self._data:
            self._data[GLOBAL_KEY] = {}
        del self._data[key]
        await self.save()

    async def pop_global(self, key, default=None):
        """Removes and returns a global value"""
        if GLOBAL_KEY not in self._data:
            self._data[GLOBAL_KEY] = {}
        value = self._data[GLOBAL_KEY].pop(key, default)
        await self.save()
        return value