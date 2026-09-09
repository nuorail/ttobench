import os

import json_strict

# A journey may place a timing point at an explicit position instead of naming
# one of the track's. That escape hatch is not meant to restate a position the
# track already records, so an explicit position that lands exactly on a named
# timing point of the track is rejected. The tolerance only absorbs the unit
# conversion; it is deliberately far smaller than any real spacing between a
# station and a nearby benchmark waypoint.
POSITION_TOLERANCE = 1e-6  # m


class JourneyValidator():

    def __init__(self):

        self.required_fields = {'metadata', 'timing points'}

        self.optional_fields = set()

        self.required_metadata = {'id', 'associated track', 'library version'}

        self.optional_metadata = {'description', 'created by', 'license'}

        self.point_types = {'stopping', 'passing'}

        self.bound_keys = {'stopping': ('arrival', 'departure'), 'passing': ('time', 'speed')}

        self.journey_data = None

        self.track_data = None


    def validate_journey(self, filename, tracks_dir="../tracks"):

        self.load_json(filename)

        self.validate_keys()

        self.validate_metadata()

        self.load_associated_track(tracks_dir)

        self.validate_timing_points()


    def load_json(self, filename):

        try:

            data = json_strict.load(filename)

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


    def load_associated_track(self, tracks_dir):

        metadata = self.journey_data['metadata']

        track_id = metadata['associated track']
        journey_id = metadata['id']

        if type(track_id) is not str:

            raise ValueError("Unexpected value type in 'associated track'! Expecting str.")

        if not journey_id.startswith(track_id + "_"):

            raise ValueError("Journey ID must start with associated track ID followed by '_'!")

        track_filename = os.path.join(tracks_dir, track_id + ".json")

        try:

            self.track_data = json_strict.load(track_filename)

        except FileNotFoundError:

            raise FileNotFoundError("Associated track file not found: {}!".format(track_id))


    def track_length(self):
        "Length of the associated track in meters."

        length = self.track_data['length']

        return self.to_meter(length['value'], length['unit'])


    def track_timing_points(self):
        """The timing points of the associated track, positions in meters.

        'timing points' is optional in a track: when it is absent the track has
        two implicit, unnamed timing points, at 0 and at its length.
        """

        if 'timing points' not in self.track_data:

            return [{'position': 0.0}, {'position': self.track_length()}]

        timing_points = self.track_data['timing points']
        unit = timing_points['units']['position']

        points = []

        for point in timing_points['values']:

            converted = dict(point)
            converted['position'] = self.to_meter(point['position'], unit)
            points.append(converted)

        return points


    def validate_units(self):

        timing_points = self.journey_data['timing points']

        fields = {'units', 'values'}

        if fields != timing_points.keys():

            raise ValueError("Unexpected keys in 'timing points'! Expecting 'units' and 'values'.")

        units = timing_points['units']

        fields_units = {'position', 'time', 'speed'}

        if fields_units != units.keys():

            raise ValueError("Unexpected keys in units of 'timing points'! Expecting 'position', 'time' and 'speed'.")

        if units['position'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in position of 'timing points'! Expecting 'm' or 'km'.")

        if units['time'] not in {'s'}:

            raise ValueError("Unexpected unit in time of 'timing points'! Expecting 's'.")

        if units['speed'] not in {'km/h', 'm/s'}:

            raise ValueError("Unexpected unit in speed of 'timing points'! Expecting 'km/h' or 'm/s'.")


    def validate_bounds(self, key, bounds, index):
        "Check one [lower, upper] constraint pair. Either bound may be null."

        if type(bounds) is not list or len(bounds) != 2:

            raise ValueError("Unexpected value for '{}' in timing point {}! Expecting a list of two entries, [lower, upper].".format(key, index+1))

        lower, upper = bounds

        for bound, label in zip(bounds, ['lower', 'upper']):

            if bound is not None and type(bound) not in {float, int}:

                raise ValueError("Unexpected value type in {} bound of '{}' in timing point {}! Expecting float, int or None, found {}.".format(label, key, index+1, type(bound)))

            if bound is not None and bound < 0:

                raise ValueError("Bounds of '{}' in timing point {} must be positive or None!".format(key, index+1))

        if lower is not None and upper is not None and lower > upper:

            raise ValueError("Lower bound of '{}' must be smaller than or equal to its upper bound! Error at timing point {}.".format(key, index+1))


    def resolve_position(self, point, index, track_points):
        """The position of one journey timing point, in meters.

        A timing point locates itself either by naming a timing point of the
        associated track, or by carrying an explicit position of its own.
        """

        has_name = 'name' in point
        has_position = 'position' in point

        if has_name == has_position:

            raise ValueError("Timing point {} must have exactly one of 'name' and 'position'!".format(index+1))

        if has_name:

            name = point['name']

            if type(name) is not str:

                raise ValueError("Unexpected value type in 'name' of timing point {}! Expecting str, found {}.".format(index+1, type(name)))

            for track_point in track_points:

                if track_point.get('name') == name:

                    return track_point['position']

            known = ", ".join(sorted(repr(p['name']) for p in track_points if 'name' in p))

            raise ValueError("Timing point {} refers to '{}', which is not a named timing point of track '{}'! Known names: {}.".format(
                index+1, name, self.journey_data['metadata']['associated track'], known if known else "none"))

        position = point['position']

        if type(position) not in {float, int}:

            raise ValueError("Unexpected value type in 'position' of timing point {}! Expecting float or int, found {}.".format(index+1, type(position)))

        if position < 0:

            raise ValueError("Position of timing point {} must be positive!".format(index+1))

        position = self.to_meter(position, self.journey_data['timing points']['units']['position'])

        if position > self.track_length():

            raise ValueError("Position of timing point {} must be smaller than or equal to the track length!".format(index+1))

        for track_point in track_points:

            if 'name' in track_point and abs(track_point['position'] - position) <= POSITION_TOLERANCE:

                raise ValueError("Timing point {} gives an explicit position that is the position of '{}' on track '{}'! Refer to it by name instead of restating where it is.".format(
                    index+1, track_point['name'], self.journey_data['metadata']['associated track']))

        return position


    def validate_timing_points(self):

        self.validate_units()

        values = self.journey_data['timing points']['values']

        if type(values) is not list:

            raise ValueError("Unexpected type for values of 'timing points'! Expecting a list, found {}.".format(type(values)))

        if len(values) < 2:

            raise ValueError("'timing points' must contain at least two entries!")

        track_points = self.track_timing_points()

        positions = []

        for ii, point in enumerate(values):

            if type(point) is not dict:

                raise ValueError("Unexpected entry type in 'timing points'! Expecting a dictionary, found {}.".format(type(point)))

            if 'type' not in point:

                raise ValueError("Missing 'type' in timing point {}! Expecting one of {}.".format(ii+1, ", ".join(sorted(repr(t) for t in self.point_types))))

            point_type = point['type']

            if point_type not in self.point_types:

                raise ValueError("Unknown 'type' in timing point {}: {}! Expecting one of {}.".format(ii+1, repr(point_type), ", ".join(sorted(repr(t) for t in self.point_types))))

            first_bound, second_bound = self.bound_keys[point_type]

            unknown_keys = set(point) - {'type', 'name', 'position', first_bound, second_bound}

            if unknown_keys:

                raise ValueError("Unknown key(s) in timing point {}: {}! A '{}' timing point takes 'type', 'name' or 'position', '{}' and '{}'.".format(
                    ii+1, ", ".join(sorted(unknown_keys)), point_type, first_bound, second_bound))

            positions.append(self.resolve_position(point, ii, track_points))

            for key in (first_bound, second_bound):

                if key in point:

                    self.validate_bounds(key, point[key], ii)

            is_first = ii == 0
            is_last = ii == len(values) - 1

            if point_type == 'stopping':

                self.validate_stopping_point(point, ii, is_first, is_last)

            else:

                if is_first or is_last:

                    raise ValueError("The first and last timing point must be of type 'stopping'! Error at timing point {}.".format(ii+1))

                if point.get('speed') == [0, 0]:

                    raise ValueError("A 'passing' timing point must not have both speed bounds set to zero! Use type 'stopping' instead. Error at timing point {}.".format(ii+1))

            if ii > 0 and positions[ii] <= positions[ii-1]:

                raise ValueError("Positions in 'timing points' must be strictly increasing! Error at timing point {}.".format(ii+1))


    def validate_stopping_point(self, point, index, is_first, is_last):
        """Arrival and departure of a stopping point.

        The first timing point of a journey is only departed from and the last
        one is only arrived at; every stopping point in between both ends the
        journey section that reaches it and begins the next one, so it carries
        an arrival and a departure whose difference is the dwell time.
        """

        if is_first and 'arrival' in point:

            raise ValueError("The first timing point is a departure and must not have an 'arrival'!")

        if is_first and 'departure' not in point:

            raise ValueError("The first timing point must have a 'departure'!")

        if is_last and 'departure' in point:

            raise ValueError("The last timing point is an arrival and must not have a 'departure'!")

        if is_last and 'arrival' not in point:

            raise ValueError("The last timing point must have an 'arrival'!")

        if not is_first and not is_last:

            for key in ('arrival', 'departure'):

                if key not in point:

                    raise ValueError("Intermediate stopping point {} must have both an 'arrival' and a 'departure'! Missing: '{}'.".format(index+1, key))

            for jj, label in enumerate(['lower', 'upper']):

                arrival, departure = point['arrival'][jj], point['departure'][jj]

                if arrival is not None and departure is not None and departure < arrival:

                    raise ValueError("The {} departure bound of stopping point {} is earlier than its {} arrival bound, giving a negative dwell time!".format(label, index+1, label))


    def journey_sections(self):
        """Index pairs (departure, arrival) delimiting the journey sections.

        A journey section is the part of a journey between two consecutive
        stopping points.
        """

        values = self.journey_data['timing points']['values']

        stopping = [ii for ii, point in enumerate(values) if point['type'] == 'stopping']

        return list(zip(stopping[:-1], stopping[1:]))


if __name__ == '__main__':

    validator = JourneyValidator()

    journeys_dir = "../journeys"

    for file in os.listdir(journeys_dir):

        if file.endswith(".json"):

            id, _ = os.path.splitext(file)

            print("Validating journey: {}".format(id))

            validator.validate_journey(os.path.join(journeys_dir, file))

            print("ok")
