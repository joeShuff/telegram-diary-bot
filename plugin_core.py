import inspect
import json
from pathlib import Path

from telegram import Message
from telegram.ext import Application

import importlib
import os
import pkgutil


class BasePlugin:
    def get_id(self) -> str:
        raise NotImplementedError

    def load(self, application):
        """
        Called when the plugin is loaded.
        'application' is the python-telegram-bot Application object.
        Use it to register commands, handlers, etc.
        """
        raise NotImplementedError()

    def on_entry(self, source_message: Message, transcription_path, voice_note_path, diary_entry: str):
        raise NotImplementedError

    def save_config(self, user_id: int, data: any):
        save_user_config(user_id, self.get_id(), data)

    def load_config(self, user_id: int) -> dict:
        return get_user_config(user_id, self.get_id())


PLUGIN_ENV = os.getenv("ENABLED_PLUGINS", "")  # e.g. "pluginone,plugintwo"
ENABLED_PLUGIN_IDS = {p.strip() for p in PLUGIN_ENV.split(",") if p.strip()}

plugins = []


def load_plugins(application: Application):
    global plugins
    plugins = []

    package = "plugins"

    for _, module_name, _ in pkgutil.iter_modules([package]):
        module_path = f"{package}.{module_name}"
        mod = importlib.import_module(module_path)

        # Find all classes in the module that inherit from BasePlugin
        for _, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                plugin_instance = obj()
                plugin_id = plugin_instance.get_id()

                if plugin_id in ENABLED_PLUGIN_IDS:
                    print(f"[PluginCore] Enabled plugin: {plugin_id}")
                    plugin_instance.load(application)
                    plugins.append(plugin_instance)
                else:
                    print(f"[PluginCore] Disabled plugin: {plugin_id}")


async def run_plugins(source_message, transcription_path, voice_note_path, diary_entry):
    global plugins

    for plugin in plugins:
        try:
            print(f"[PluginCore] Running plugin {plugin.get_id()}")
            await plugin.on_entry(source_message, transcription_path, voice_note_path, diary_entry)
        except Exception as e:
            print(f"[PluginCore] Plugin {plugin.get_id()} failed: {e}")


from const import CONFIG_PATH
CONFIG_FILE = Path(CONFIG_PATH + "/plugin_config.json")


def load_all_configs():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_all_configs(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def save_user_config(user_id: str, plugin_id: str, data):
    # Verify parcelable
    try:
        json.dumps(data)
    except Exception as e:
        raise ValueError(f"Plugin data must be JSON-serializable: {e}")

    cfg = load_all_configs()
    cfg.setdefault(str(user_id), {})
    cfg[str(user_id)][plugin_id] = data
    save_all_configs(cfg)


def get_user_config(user_id: str, plugin_id: str):
    cfg = load_all_configs()
    return cfg.get(str(user_id), {}).get(plugin_id)

