import os
import json


class JourneyValidator():

    def __init__(self):

        self.required_fields = {'metadata', 'timing points'}

        self.optional_fields = set()

        self.required_metadata = {'id', 'associated track', 'library version'}

        self.optional_metadata = {'description', 'created by', 'license'}

        self.journey_data = None


    def validate_journey(self, filename, tracks_dir="../tracks"):

        self.load_json(filename)

        self.validate_keys()

        self.validate_metadata()

        self.validate_timing_points()

        self.validate_associated_track(tracks_dir)


    def load_json(self, filename):

        try:

            with open(filename) as file:

                data = json.load(file)

        except FileNotFoundError:

            raise FileNotFoundError("Specified journey file not found!")

        self.journey_data = data
        self.filename = filename


    def validate_keys(self):
        "Check that all required keys are there and that there are no redundant fields."

        data = self.journey_data

        required_fields = set()

        for key in data.keys():

            if key in self.required_fields:

                required_fields.add(key)

            elif key not in self.optional_fields:

                raise ValueError("Unknown field detected: {}'!".format(key))

        if required_fields != self.required_fields:

            missing = ", ".join([f"'{item}'" for item in self.required_fields-required_fields])
            output = f"Not all required fields found! Missing: {missing}!"

            raise ValueError(output)


    def validate_metadata(self):

        metadata = self.journey_data['metadata']

        required_metadata = set()

        for key in metadata.keys():

            if key in self.required_metadata:

                required_metadata.add(key)

            elif key not in self.optional_metadata:

                raise ValueError("Unknown field detected in metadata: {}'!".format(key))

        if required_metadata != self.required_metadata:

            missing_metadata = ", ".join([f"'{item}'" for item in self.required_metadata-required_metadata])
            output_metadata = f"Not all required fields found in metadata! Missing: {missing_metadata}!"

            raise ValueError(output_metadata)

        journey_ID, _ = os.path.splitext(self.filename.split(os.path.sep)[-1])

        if journey_ID != metadata['id']:

            raise ValueError("Inconsistent ID between filename and metadata!")


    def to_meter(self, value, unit):

        if unit == 'km':
            return 1000 * value

        return value


    def validate_associated_track(self, tracks_dir):

        metadata = self.journey_data['metadata']

        track_id = metadata['associated track']
        journey_id = metadata['id']

        if type(track_id) is not str:

            raise ValueError("Unexpected value type in 'associated track'! Expecting str.")

        if not journey_id.startswith(track_id + "_"):

            raise ValueError("Journey ID must start with associated track ID followed by '_'!")

        track_filename = os.path.join(tracks_dir, track_id + ".json")

        try:

            with open(track_filename) as file:

                track_data = json.load(file)

        except FileNotFoundError:

            raise FileNotFoundError("Associated track file not found: {}!".format(track_id))

        arrival_position = self.journey_data['timing points']['values'][-1][0]
        departure_unit = self.journey_data['timing points']['units']['position']

        track_length = track_data['stops']['values'][-1]
        track_length_unit = track_data['stops']['unit']

        arrival_position = self.to_meter(arrival_position, departure_unit)
        track_length = self.to_meter(track_length, track_length_unit)

        if arrival_position > track_length:
            raise ValueError("Arrival position must be smaller than or equal to the track length!")


    def is_stopping_point(self, timing_point):

        return timing_point[3] == 0 and timing_point[4] == 0

    def get_journey_section_bounds(self, values):

        departures = [0]
        arrivals = []

        for ii in range(1, len(values)):

            if values[ii][0] == values[ii-1][0]:

                arrivals.append(ii-1)
                departures.append(ii)

        arrivals.append(len(values)-1)

        return list(zip(departures, arrivals))


    def validate_timing_points(self):

        timing_points = self.journey_data['timing points']

        fields = {'units', 'values'}

        if fields != timing_points.keys():

            raise ValueError("Unexpected keys in 'timing points'! Expecting 'units' and 'values'.")

        fields_units = {
            'position',
            'lower time constraint',
            'upper time constraint',
            'lower speed constraint',
            'upper speed constraint'
        }

        if fields_units != timing_points['units'].keys():

            raise ValueError("Unexpected keys in units of 'timing points'!")

        if timing_points['units']['position'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in position of 'timing points'! Expecting 'm' or 'km'.")

        if timing_points['units']['lower time constraint'] not in {'s'} or timing_points['units']['upper time constraint'] not in {'s'}:

            raise ValueError("Unexpected unit in time constraints of 'timing points'! Expecting 's'.")

        if timing_points['units']['lower speed constraint'] not in {'km/h', 'm/s'} or timing_points['units']['upper speed constraint'] not in {'km/h', 'm/s'}:

            raise ValueError("Unexpected unit in speed constraints of 'timing points'! Expecting 'km/h' or 'm/s'.")

        values = timing_points['values']

        if len(values) < 2:

            raise ValueError("'timing points' must contain at least two entries!")

        for ii, v in enumerate(values):

            if len(v) != 5:
                raise ValueError(
                    "Unexpected size of nested list in 'timing points'! Expecting 5, got {}.".format(len(v)))

            pos, t_min, t_max, v_min, v_max = v

            if type(pos) not in {float, int}:

                raise ValueError("Unexpected value type in position of 'timing points'! Expecting float or int, found {}.".format(type(pos)))

            if pos < 0:

                raise ValueError("Position of 'timing points' must be positive!")

            if ii > 0 and pos < values[ii-1][0]:

                raise ValueError("Positions in 'timing points' must be non-decreasing! Error at point {}.".format(ii+1))

            if ii > 0 and pos == values[ii - 1][0]:

                if ii == 1 or ii == len(values) - 1:

                    raise ValueError("Equal positions are only allowed for intermediate arrival/departure pairs! Error at point {}.".format(ii + 1))

                if not self.is_stopping_point(v) or not self.is_stopping_point(values[ii - 1]):

                    raise ValueError("Equal positions are only allowed for consecutive stopping points! Error at point {}.".format(ii + 1))

                if ii > 1 and pos == values[ii - 2][0]:

                    raise ValueError("More than two consecutive timing points at the same position are not allowed! Error at point {}.".format(ii + 1))

            for key, value in zip(
                    ['lower time constraint', 'upper time constraint', 'lower speed constraint',
                     'upper speed constraint'],
                    [t_min, t_max, v_min, v_max]
            ):

                if value is not None and type(value) not in {float, int}:

                    raise ValueError("Unexpected value type in '{}' of 'timing points'! Expecting float, int or None, found {}.".format(key, type(value)))

                if value is not None and value < 0:

                    raise ValueError("'{}' of 'timing points' must be positive or None!".format(key))

            if t_min is not None and t_max is not None and t_min > t_max:

                raise ValueError("Lower time constraint must be smaller than or equal to upper time constraint! Error at point {}.".format(ii+1))

            if v_min is not None and v_max is not None and v_min > v_max:

                raise ValueError("Lower speed constraint must be smaller than or equal to upper speed constraint! Error at point {}.".format(ii+1))

            if ii == 0 or ii == len(values)-1:

                if v_min != 0 or v_max != 0:

                    raise ValueError("First and last timing point must have both speed constraints set to zero!")

        for ii, v in enumerate(values):

            if ii == 0 or ii == len(values) - 1:

                continue

            if self.is_stopping_point(v):

                pos = v[0]

                if pos != values[ii - 1][0] and pos != values[ii + 1][0]:

                    raise ValueError("Intermediate stopping points must be part of an arrival/departure pair! Error at point {}.".format(ii + 1))

        journey_section_bounds = self.get_journey_section_bounds(values)

        if len(journey_section_bounds) < 1:

            raise ValueError("Journey must contain at least one journey section!")

        for ii, bounds in enumerate(journey_section_bounds):

            departure_idx, arrival_idx = bounds

            if departure_idx >= arrival_idx:

                raise ValueError("Invalid journey section {}!".format(ii))

            if not self.is_stopping_point(values[departure_idx]) or not self.is_stopping_point(values[arrival_idx]):

                raise ValueError("Journey section {} must start and end with a stopping point!".format(ii))

            if values[departure_idx][0] >= values[arrival_idx][0]:

                raise ValueError("Journey section {} must have increasing position!".format(ii))


if __name__ == '__main__':

    validator = JourneyValidator()

    journeys_dir = "../journeys"

    for file in os.listdir(journeys_dir):

        if file.endswith(".json"):

            id, _ = os.path.splitext(file)

            print("Validating journey: {}".format(id))

            validator.validate_journey(os.path.join(journeys_dir, file))

            print("ok")