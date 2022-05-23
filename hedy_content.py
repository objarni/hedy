import copy
import os
from babel import Locale
from website.yaml_file import YamlFile
import iso3166

import random

# Define and load all countries
COUNTRIES = {k: v.name for k, v in iso3166.countries_by_alpha2.items()}

# Define dictionary for available languages. Fill dynamically later.
ALL_LANGUAGES = {}
ALL_KEYWORD_LANGUAGES = {}

# Todo TB -> We create this list manually, but it would be nice if we find a way to automate this as well
NON_LATIN_LANGUAGES = ['ar', 'bg', 'bn', 'el', 'fa', 'hi', 'ru', 'zh_Hans']

ADVENTURE_ORDER = [
    'default',
    'story',
    'parrot',
    'songs',
    'turtle',
    'dishes',
    'dice',
    'rock',
    'calculator',
    'fortune',
    'restaurant',
    'haunted',
    'piggybank',
    'quizmaster',
    'language',
    'secret',
    'tic',
    'blackjack',
    'next',
    'end'
]

# load all available languages in dict
# list_translations of babel does about the same, but without territories.
languages = {}
if not os.path.isdir('translations'):
    # should not be possible, but if it's moved someday, EN would still be working.
    ALL_LANGUAGES['en'] = 'English'
    ALL_KEYWORD_LANGUAGES['en'] = 'EN'

for folder in os.listdir('translations'):
    locale_dir = os.path.join('translations', folder, 'LC_MESSAGES')
    if not os.path.isdir(locale_dir):
        continue

    if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
        locale = Locale.parse(folder)
        languages[folder] = locale.display_name.title()

for l in sorted(languages):
    ALL_LANGUAGES[l] = languages[l]
    if os.path.exists(f'./grammars/keywords-{l}.lark'):
        ALL_KEYWORD_LANGUAGES[l] = l[:2].upper()

# Load and cache all keyword yamls
KEYWORDS = {}
for lang in ALL_KEYWORD_LANGUAGES:
    KEYWORDS[lang] = dict(YamlFile.for_file(f'content/keywords/{lang}.yaml'))
    for k, v in KEYWORDS[lang].items():
        if type(v) == str and "|" in v:
            # when we have several options, pick the first one as default
            KEYWORDS[lang][k] = v.split('|')[0]


class Commands:
    # Want to parse the keywords only once, they can be cached -> perform this action on server start
    def __init__(self, language):
        self.language = language
        # We can keep these cached, even in debug_mode: files are small and don't influence start-up time much
        self.file = YamlFile.for_file(f'content/commands/{self.language}.yaml')
        self.data = {}

        # For some reason the is_debug_mode() function is not (yet) ready when we call this code
        # So we call the NO_DEBUG_MODE directly from the environment
        # Todo TB -> Fix that the is_debug_mode() function is ready before server start
        self.debug_mode = not os.getenv('NO_DEBUG_MODE')

        if not self.debug_mode:
            # We always create one with english keywords
            self.data["en"] = self.cache_keyword_parsing("en")
            if language in ALL_KEYWORD_LANGUAGES.keys():
                self.data[language] = self.cache_keyword_parsing(language)

    def cache_keyword_parsing(self, language):
        keyword_data = {}
        for level in copy.deepcopy(self.file):
            # Take a copy -> otherwise we overwrite the parsing
            commands = copy.deepcopy(self.file.get(level))
            for command in commands:
                for k, v in command.items():
                    try:
                        command[k] = v.format(**KEYWORDS.get(language))
                    except IndexError:
                        print("There is an issue due to an empty placeholder in the following line:")
                        print(v)
                    except KeyError:
                        print("There is an issue due to a non-existing key in the following line:")
                        print(v)
            keyword_data[level] = commands
        return keyword_data

    def get_commands_for_level(self, level, keyword_lang="en"):
        if self.debug_mode and not self.data.get(keyword_lang, None):
            self.data[keyword_lang] = self.cache_keyword_parsing(keyword_lang)
        return self.data.get(keyword_lang, {}).get(int(level), None)


# Todo TB -> We don't need these anymore as we guarantee with Weblate that each language file is there


class NoSuchCommand:
    def get_commands_for_level(self, level, keyword_lang):
        return {}

class Adventures:
    def __init__(self, language):
        self.language = language
        self.file = {}
        self.data = {}

        # For some reason the is_debug_mode() function is not (yet) ready when we call this code
        # So we call the NO_DEBUG_MODE directly from the environment
        # Todo TB -> Fix that the is_debug_mode() function is ready before server start
        self.debug_mode = not os.getenv('NO_DEBUG_MODE')

        if not self.debug_mode:
            self.file = YamlFile.for_file(
                f'content/adventures/{self.language}.yaml').get('adventures')
            # We always create one with english keywords
            self.data["en"] = self.cache_adventure_keywords("en")
            if language in ALL_KEYWORD_LANGUAGES.keys():
                self.data[language] = self.cache_adventure_keywords(language)

    def cache_adventure_keywords(self, language):
        # Sort the adventure to a fixed structure to make sure they are structured the same for each language
        sorted_adventures = {
            adventure_index: (self.file.get(adventure_index))
            for adventure_index in ADVENTURE_ORDER
            if self.file.get(adventure_index, None)
        }

        self.file = sorted_adventures
        keyword_data = {}
        for short_name, adventure in self.file.items():
            parsed_adventure = copy.deepcopy(adventure)
            for level in adventure.get('levels'):
                for k, v in adventure.get('levels').get(level).items():
                    try:
                        parsed_adventure.get('levels').get(level)[k] = v.format(**KEYWORDS.get(language))
                    except IndexError:
                        print("There is an issue due to an empty placeholder in the following line:")
                        print(v)
                    except KeyError:
                        print("There is an issue due to a non-existing key in the following line:")
                        print(v)
            keyword_data[short_name] = parsed_adventure
        return keyword_data

    # Todo TB -> We can also cache this; why not?
    # When customizing classes we only want to retrieve the name, (id) and level of each adventure
    def get_adventure_keyname_name_levels(self):
        if self.debug_mode and not self.data.get("en", None):
            if not self.file:
                self.file = YamlFile.for_file(
                    f'content/adventures/{self.language}.yaml').get('adventures')
            self.data["en"] = self.cache_adventure_keywords("en")
        return {
            adventure[0]: {
                adventure[1]['name']: list(adventure[1]['levels'].keys())
            }
            for adventure in self.data["en"].items()
        }

    # Todo TB -> We can also cache this; why not?
    # When filtering on the /explore or /programs page we only want the actual names
    def get_adventure_names(self):
        if self.debug_mode and not self.data.get("en", None):
            if not self.file:
                self.file = YamlFile.for_file(
                    f'content/adventures/{self.language}.yaml').get('adventures')
            self.data["en"] = self.cache_adventure_keywords("en")
        return {
            adventure[0]: adventure[1]['name']
            for adventure in self.data["en"].items()
        }

    def get_adventures(self, keyword_lang="en"):
        if self.debug_mode and not self.data.get(keyword_lang, None):
            if not self.file:
                self.file = YamlFile.for_file(
                    f'content/adventures/{self.language}.yaml').get('adventures')
            self.data[keyword_lang] = self.cache_adventure_keywords(
                keyword_lang)
        return self.data.get(keyword_lang)

    def has_adventures(self):
        if self.debug_mode and not self.data.get("en", None):
            if not self.file:
                self.file = YamlFile.for_file(
                    f'content/adventures/{self.language}.yaml').get('adventures')
            self.data["en"] = self.cache_adventure_keywords("en")
        return bool(self.data.get("en"))     
      
# Todo TB -> We don't need these anymore as we guarantee with Weblate that each language file is there
class NoSuchAdventure:
  def get_adventure(self):
    return {}
  

class ParsonsProblem:
    def __init__(self, language):
        self.language = language
        self.file = {}
        self.data = {}

        self.debug_mode = not os.getenv('NO_DEBUG_MODE')

        if not self.debug_mode:
            self.file = YamlFile.for_file(f'content/parsons/{self.language}.yaml').get('parsons')
            # We always create one with english keywords
            self.data["en"] = self.cache_parsons_keywords("en")
            if language in ALL_KEYWORD_LANGUAGES.keys():
                self.data[language] = self.cache_parsons_keywords(language)

    def cache_parsons_keywords(self, language):
        keyword_data = {}
        for short_name, parson in self.file.items():
            parsed_parson = copy.deepcopy(parson)
            for level in parson.get('levels'):
                for k, v in parson.get('levels').get(level).get('code_lines').items():
                    try:
                        parsed_parson.get('levels').get(level).get('code_lines')[k] = v.format(**KEYWORDS.get(language))
                    except IndexError:
                        print("There is an issue due to an empty placeholder in the following line:")
                        print(v)
                    except KeyError:
                        print("There is an issue due to a non-existing key in the following line:")
                        print(v)
            keyword_data[short_name] = parsed_parson
        return keyword_data

    def get_parsons(self, keyword_lang="en"):
        if self.debug_mode and not self.data.get(keyword_lang, None):
            if not self.file:
                self.file = YamlFile.for_file(f'content/parsons/{self.language}.yaml').get('parsons')
            self.data[keyword_lang] = self.cache_parsons_keywords(keyword_lang)
        return self.data.get(keyword_lang)


class Quizzes:
    def __init__(self, language):
        self.language = language
        self.file = {}
        self.data = {}

        # For some reason the is_debug_mode() function is not (yet) ready when we call this code
        # So we call the NO_DEBUG_MODE directly from the environment
        # Todo TB -> Fix that the is_debug_mode() function is ready before server start
        self.debug_mode = not os.getenv('NO_DEBUG_MODE')

        if not self.debug_mode:
            self.file = YamlFile.for_file(f'content/quizzes/{self.language}.yaml').to_dict()
            self.data["en"] = self.cache_quiz_keywords("en")
            if language in ALL_KEYWORD_LANGUAGES.keys():
                self.data[language] = self.cache_quiz_keywords(language)

    def cache_quiz_keywords(self, language):
        keyword_data = {}
        for level in copy.deepcopy(self.file):
            questions = copy.deepcopy(self.file.get(level))
            for number, question in questions.items():
                for k, v in question.items():
                    # We have to parse another way for the mp_choice_options
                    if k == "mp_choice_options":
                        options = []
                        for option in copy.deepcopy(v):
                            temp = {
                                key: value.format(**KEYWORDS.get(language))
                                for key, value in option.items()
                            }

                            options.append(temp)
                        questions[number][k] = options
                    else:
                        questions[number][k] = v.format(**KEYWORDS.get(language))
            keyword_data[level] = questions
        return keyword_data

    def get_highest_question_level(self, level):
        if self.debug_mode and not self.data.get("en", None):
            if not self.file:
                self.file = YamlFile.for_file(f'content/quizzes/{self.language}.yaml').get('levels')
            self.data["en"] = self.cache_quiz_keywords("en")
        return len(self.data["en"].get(level, {}))

    def get_quiz_data_for_level(self, level, keyword_lang="en"):
        # We want to keep the keyword language as english until the questions are adjusted for dynamic keywords
        keyword_lang = "en"

        if self.debug_mode and not self.data.get(keyword_lang, None):
            if not self.file:
                self.file = YamlFile.for_file(f'content/quizzes/{self.language}.yaml').get('levels')
            self.data[keyword_lang] = self.cache_quiz_keywords(keyword_lang)
        return self.data.get(keyword_lang, {}).get(level, None)

    def get_quiz_data_for_level_question(self, level, question, keyword_lang="en"):
        # We want to keep the keyword language as english until the questions are adjusted for dynamic keywords
        keyword_lang = "en"

        if self.debug_mode and not self.data.get(keyword_lang, None):
            if not self.file:
                self.file = YamlFile.for_file(f'content/quizzes/{self.language}.yaml').get('levels')
            self.data[keyword_lang] = self.cache_quiz_keywords(keyword_lang)
        return self.data.get(keyword_lang, {}).get(level, {}).get(question, None)


class NoSuchQuiz:
    def get_quiz_data_for_level(self, level, keyword_lang):
        return {}
