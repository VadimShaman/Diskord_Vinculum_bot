import discord
from discord.ext import commands
import json
import os
import random
from typing import Dict, List

class RelationshipSystem:
    def __init__(self):
        self.characters_file = "characters.json"
        self.relationships_file = "relationships.json"
        self.load_data()

    def load_data(self):
        # Загрузка персонажей
        if os.path.exists(self.characters_file):
            with open(self.characters_file, "r", encoding="utf-8") as f:
                self.characters = json.load(f)
        else:
            self.characters = {}

        # Загрузка отношений
        if os.path.exists(self.relationships_file):
            with open(self.relationships_file, "r", encoding="utf-8") as f:
                self.relationships = json.load(f)
        else:
            self.relationships = {}

    def save_data(self):
        with open(self.characters_file, "w", encoding="utf-8") as f:
            json.dump(self.characters, f, ensure_ascii=False, indent=2)
        with open(self.relationships_file, "w", encoding="utf-8") as f:
            json.dump(self.relationships, f, ensure_ascii=False, indent=2)