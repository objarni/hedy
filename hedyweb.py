import collections

from flask_babel import gettext

from website.yaml_file import YamlFile
import attr
import glob
from os import path
from flask_helpers import render_template
from website.auth import current_user, is_teacher
import utils


class AchievementTranslations:
    def __init__(self):
        self.data = {}

        translations = glob.glob('content/achievements/*.yaml')
        for trans_file in translations:
            lang = path.splitext(path.basename(trans_file))[0]
            self.data[lang] = YamlFile.for_file(trans_file)

    def get_translations(self, language):
        d = collections.defaultdict(lambda: 'Unknown Exception')
        d.update(**self.data.get('en', {}))
        d.update(**self.data.get(language, {}))
        return d


class PageTranslations:
    def __init__(self, page):
        self.data = {}
        if page in ['start', 'learn-more', 'for-teachers']:
            translations = glob.glob('content/pages/*.yaml')
        else:
            translations = glob.glob(f'content/pages/{page}/*.yaml')
        for file in translations:
            lang = path.splitext(path.basename(file))[0]
            self.data[lang] = YamlFile.for_file(file)

    def exists(self):
        """Whether or not any content was found for this page."""
        return len(self.data) > 0

    def get_page_translations(self, language):
        d = collections.defaultdict(lambda: '')
        d.update(**self.data.get('en', {}))
        d.update(**self.data.get(language, {}))
        return d


def render_code_editor_with_tabs(commands, max_level, level_number, version, quiz, loaded_program, adventures, parsons, customizations, hide_cheatsheet, enforce_developers_mode, teacher_adventures, adventure_name):

    arguments_dict = {
        'level_nr': str(level_number),
        'level': level_number,
        'current_page': 'hedy',
        'prev_level': int(level_number) - 1 if int(level_number) > 1 else None,
        'next_level': int(level_number) + 1
        if int(level_number) < max_level
        else None,
        'customizations': customizations,
        'hide_cheatsheet': hide_cheatsheet,
        'enforce_developers_mode': enforce_developers_mode,
        'teacher_adventures': teacher_adventures,
        'loaded_program': loaded_program,
        'adventures': adventures,
        'parsons': parsons,
        'adventure_name': adventure_name,
        'latest': version,
        'quiz': quiz,
    }


    return render_template("code-page.html", **arguments_dict, commands=commands)


def render_tutorial_mode(level, commands, adventures):
    arguments_dict = {
        'tutorial': True,
        'next_level': 2,
        'level_nr': str(level),
        'level': str(level),
        'adventures': adventures,
        'quiz': True,
    }


    return render_template("code-page.html", **arguments_dict, commands=commands)

def render_specific_adventure(level_number, adventure, version, prev_level, next_level):
    arguments_dict = {
        'specific_adventure': True,
        'level_nr': str(level_number),
        'level': level_number,
        'prev_level': prev_level,
        'next_level': next_level,
        'customizations': [],
        'hide_cheatsheet': None,
        'enforce_developers_mode': None,
        'teacher_adventures': [],
        'adventures': adventure,
        'latest': version,
    }


    return render_template("code-page.html", **arguments_dict)
