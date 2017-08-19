# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import os
import re
import yaml

import lib.genanki.genanki as genanki

class Anki:
    def generate_id():
        """Generate a 32-bit ID useful for Anki."""
        return random.randrange(1 << 30, 1 << 31)
        # return datetime.now().timestamp()

    def import_card_definitions(self, yaml_filepath):
        """Import card definitions from YAML file.

        Adds a Anki-like {{import:file.txt}} file import command which
        works similar to the #include preprocessor command in C-like
        languages, directly replacing the command with text from the
        import file.
        """
        path = os.path.dirname(yaml_filepath) + '/'
        with open(yaml_filepath, 'r') as f:
            cards = f.read()
            cards = yaml.load(cards)
        for subject, model in cards.items():
            for template in model['templates']:
                for fmt in ('qfmt', 'afmt'):
                    with open(path + template[fmt], 'r') as f:
                        lines = f.readlines()
                    temp = ''
                    for line in lines:
                        match = re.match('\s*{{import:(.*)}}', line)
                        if match:
                            with open(path + match.group(1), 'r') as f:
                                line = f.read()
                        temp += line
                    template[fmt] = temp
        return cards
