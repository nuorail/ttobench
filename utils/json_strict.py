"""JSON loading that rejects duplicate keys.

`json.load()` silently keeps the last value when an object repeats a key, so a
file carrying two `altitude` fields parses without complaint and then validates
without complaint — the reader sees one of the two values and no reader can
tell which was intended. RFC 8259 says the names in an object SHOULD be unique
and that behavior is unpredictable when they are not, so the library treats a
repeated key as a broken file rather than picking a winner.

The check runs on every object at every depth, so it also catches a repeated
`position` inside one timing point, or a repeated unit inside `units`.
"""

import json


def _reject_duplicate_keys(pairs):

    obj = {}

    for key, value in pairs:

        if key in obj:

            raise ValueError("Duplicate key '{}' detected! A JSON object must not repeat a key.".format(key))

        obj[key] = value

    return obj


def load(filename):
    "Parse the JSON file at 'filename', raising ValueError on any duplicate key."

    with open(filename, encoding="utf-8") as file:

        return json.load(file, object_pairs_hook=_reject_duplicate_keys)
