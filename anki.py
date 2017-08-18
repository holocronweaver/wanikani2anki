# This Source Code Form is subject to the terms of the Mozilla Public
# License, v2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.
import lib.genanki.genanki as genanki

class Anki:
    def generate_id():
        """Generate a 32-bit ID useful for Anki."""
        return random.randrange(1 << 30, 1 << 31)
        # return datetime.now().timestamp()
