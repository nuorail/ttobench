"""Validate every track, train and journey in the library.

Runs the three validators over their libraries and reports every file that
fails, rather than stopping at the first one, so that a single run shows all
the problems there are to fix. Exits non-zero if any file failed.

Paths are resolved relative to this file, so the script may be run from any
directory:

    python utils/validate_all.py
"""

import os
import sys

import validate_journeys
import validate_tracks
import validate_trains


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRACKS_DIR = os.path.join(ROOT_DIR, "tracks")

TRAINS_DIR = os.path.join(ROOT_DIR, "trains")

JOURNEYS_DIR = os.path.join(ROOT_DIR, "journeys")


def validate_library(label, directory, validate):
    """Validate every JSON file in a directory, returning the failures as
    (name, error) pairs."""

    print("== {} ==".format(label))

    failures = []

    files = sorted(file for file in os.listdir(directory) if file.endswith(".json"))

    if not files:

        print("no JSON files found in {}!".format(directory))

        return [(label, ValueError("no JSON files found in {}".format(directory)))]

    for file in files:

        name, _ = os.path.splitext(file)

        try:

            validate(os.path.join(directory, file))

        except Exception as error:

            failures.append((name, error))

            print("{}: FAILED -- {}: {}".format(name, type(error).__name__, error))

        else:

            print("{}: ok".format(name))

    print("")

    return failures


def main():

    track_validator = validate_tracks.TrackValidator()

    train_validator = validate_trains.TrainValidator()

    journey_validator = validate_journeys.JourneyValidator()

    failures = []

    failures += validate_library("tracks", TRACKS_DIR, track_validator.validate_track)

    failures += validate_library("trains", TRAINS_DIR, train_validator.validate_train)

    # The journey validator loads the track each journey refers to, and looks
    # for it in the library rather than next to the journey file.
    failures += validate_library(
        "journeys",
        JOURNEYS_DIR,
        lambda filename: journey_validator.validate_journey(filename, tracks_dir=TRACKS_DIR),
    )

    if failures:

        print("{} file(s) failed validation:".format(len(failures)))

        for name, error in failures:

            print("  {}: {}: {}".format(name, type(error).__name__, error))

        return 1

    print("all files valid")

    return 0


if __name__ == '__main__':

    sys.exit(main())
