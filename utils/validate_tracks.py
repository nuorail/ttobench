import math
import os

import json


class TrackValidator():

    def __init__(self):

        self.required_fields = {'metadata', 'stops', 'speed limits'}

        self.optional_fields = {'altitude', 'gradients', 'curvatures', 'tunnels', 'ETCS braking data'}

        self.required_metadata = {'id', 'library version'}

        self.optional_metadata = {'description', 'created by', 'license'}

        self.track_data = None


    def validate_track(self, filename):

        self.load_json(filename)

        self.validate_keys()

        self.validate_metadata()

        self.validate_altitude()

        self.validate_stops()

        self.validate_speed_limits()

        self.validate_gradients()

        self.validate_curvatures()

        self.validate_tunnels()

        self.validate_etcs_braking_data()


    def load_json(self, filename):

        try:

            with open(filename) as file:

                data = json.load(file)

        except FileNotFoundError:

            raise FileNotFoundError("Specified track file not found!")

        self.track_data = data
        self.filename = filename


    def validate_keys(self):
        "Check that all required keys are there and that there are no redundant fields."

        data = self.track_data

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

        metadata = self.track_data['metadata']

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

        track_ID, _ = os.path.splitext(self.filename.split(os.path.sep)[-1])

        if track_ID != metadata['id']:

            raise ValueError("Inconsistent ID between filename and metadata!")


    def validate_altitude(self):

        altitude = self.track_data['altitude'] if 'altitude' in self.track_data else None

        if altitude is not None:

            fields = {'unit', 'value'}

            if fields != altitude.keys():

                raise ValueError("Unexpected keys in 'altitude'! Expecting 'unit' and 'value'.")

            if altitude['unit'] not in {'m', 'km'}:

                raise ValueError("Unexpected unit in 'altitude'! Expecting 'm' or 'km'.")

            if type(altitude['value']) not in {float, int}:

                raise ValueError("Unexpected value type in 'altitude'! Expecting float or int, found {}.".format(type(altitude['value'])))

            if altitude['value'] < 0:

                raise ValueError("'altitude' must be positive!")


    def validate_stops(self):

        stops = self.track_data['stops']

        fields = {'unit', 'values'}

        if fields != stops.keys():

            raise ValueError("Unexpected keys in 'stops'! Expecting 'unit' and 'values'.")

        if stops['unit'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in 'stops'! Expecting 'm' or 'km'.")

        for ii, v in enumerate(stops['values']):

            if type(v) not in {float, int}:

                raise ValueError("Unexpected value type in 'stops'! Expecting float or int, found {}.".format(type(v)))

            if v < 0:

                raise ValueError("Values in 'stops' must be positive!")

            if ii == 0:

                if v != 0:

                    raise ValueError("First value in 'stops' must be equal to zero!")

            if ii > 0 and v <= stops['values'][ii-1]:

                raise ValueError("Values in 'stops' must be strictly increasing!")


    def validate_speed_limits(self):

        speed_limits = self.track_data['speed limits']

        fields = {'units', 'values'}

        if fields != speed_limits.keys():

            raise ValueError("Unexpected keys in 'speed limits'! Expecting 'units' and 'values'.")

        fields_units = {'position', 'velocity'}

        if fields_units != speed_limits['units'].keys():

            raise ValueError("Unexpected keys in  units of 'speed limits'! Expecting 'position' and 'velocity'.")

        if speed_limits['units']['position'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in position of 'speed limits'! Expecting 'm' or 'km'.")

        if speed_limits['units']['velocity'] not in {'km/h', 'm/s'}:

            raise ValueError("Unexpected unit in velocity of 'speed limits'! Expecting 'km/h' or 'm/s'.")

        for ii, v in enumerate(speed_limits['values']):

            if len(v) != 2:

                raise ValueError("Unexpected size of nested list in 'speed limits'! Expecting 2, got {}.".format(len(v)))

            pos, vel = v

            if type(pos) not in {float, int}:

                raise ValueError("Unexpected value type in position of 'speed limits'! Expecting float or int, found {}.".format(type(pos)))

            if type(vel) not in {float, int}:

                raise ValueError("Unexpected value type in velocity of 'speed limits'! Expecting float or int, found {}.".format(type(vel)))

            if pos < 0 or vel < 0:

                raise ValueError("Position and velocity of 'speed limits' must be positive!")

            if ii == 0:

                if pos != 0:

                    raise ValueError("First position of 'speed limits' must be equal to zero!")

            if len(speed_limits['values']) > 1 and ii == len(speed_limits['values'])-1:

                if pos == self.track_data['stops']['values'][-1]:

                    raise ValueError("Last position of 'speed limits' must be smaller than the track length!")

            if ii > 0 and pos <= speed_limits['values'][ii-1][0]:

                raise ValueError("Positions in 'speed limits' must be strictly increasing! Error at point {}.".format(ii+1))


    def validate_gradients(self):

        if not 'gradients' in self.track_data:

            return

        gradients = self.track_data['gradients']

        fields = {'units', 'values'}

        if fields != gradients.keys():

            raise ValueError("Unexpected keys in 'gradients'! Expecting 'units' and 'values'.")

        fields_units = {'position', 'slope'}

        if fields_units != gradients['units'].keys():

            raise ValueError("Unexpected keys in  units of 'gradients'! Expecting 'position' and 'slope'.")

        if gradients['units']['position'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in position of 'gradients'! Expecting 'm' or 'km'.")

        if gradients['units']['slope'] not in {'permil'}:

            raise ValueError("Unexpected unit in velocity of 'gradients'! Expecting 'permil'.")

        for ii, v in enumerate(gradients['values']):

            if len(v) != 2:

                raise ValueError("Unexpected size of nested list in 'gradients'! Expecting 2, got {}.".format(len(v)))

            pos, grad = v

            if type(pos) not in {float, int}:

                raise ValueError("Unexpected value type in position of 'gradients'! Expecting float or int, found {}.".format(type(pos)))

            if type(grad) not in {float, int}:

                raise ValueError("Unexpected value type in slope of 'gradients'! Expecting float or int, found {}.".format(type(grad)))

            if pos < 0:

                raise ValueError("Position of 'gradients' must be positive!")

            if ii == 0:

                if pos != 0:

                    raise ValueError("First position of 'gradients' must be equal to zero!")

            if len(gradients['values']) > 1 and ii == len(gradients['values'])-1:

                if pos == self.track_data['stops']['values'][-1]:

                    raise ValueError("Last position of 'gradients' must be smaller than the track length!")

            if ii > 0 and pos <= gradients['values'][ii-1][0]:

                raise ValueError("Positions in 'gradients' must be strictly increasing! Error at point {}.".format(ii+1))


    def validate_curvatures(self):

        if not 'curvatures' in self.track_data:

            return

        curvatures = self.track_data['curvatures']

        fields = {'units', 'values'}

        if fields != curvatures.keys():

            raise ValueError("Unexpected keys in 'curvatures'! Expecting 'units' and 'values'.")

        fields_units = {'position', 'radius at start', 'radius at end'}

        if fields_units != curvatures['units'].keys():

            raise ValueError("Unexpected keys in units of 'curvatures'! Expecting 'position', 'radius at start' and 'radius at end'.")

        if curvatures['units']['position'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in 'position' of 'curvatures'! Expecting 'm' or 'km'.")

        if curvatures['units']['radius at start'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in 'radius at start' of 'curvatures'! Expecting 'm' or 'km'.")

        if curvatures['units']['radius at end'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in 'radius at end' of 'curvatures'! Expecting 'm' or 'km'.")

        for ii, v in enumerate(curvatures['values']):

            if len(v) != 3:

                raise ValueError("Unexpected size of nested list in 'curvatures'! Expecting 3, got {}.".format(len(v)))

            pos = v[0]

            if type(pos) not in {float, int}:

                raise ValueError("Unexpected value type in position of 'curvatures'! Expecting float or int, found {}.".format(type(pos)))

            try:

                float(v[1])

            except:

                raise ValueError("Unexpected value for 'radius at start' in 'curvatures'! Expecting a number or 'infinity' got '{}' at position {}.".format(v[1], ii))

            try:

                float(v[2])

            except:

                raise ValueError("Unexpected value for 'radius at end' in 'curvatures'! Expecting a number or 'infinity' got {} at position {}.".format(v[2], ii))

            if pos < 0:

                raise ValueError("Position of 'curvatures' must be positive!")

            if ii == 0:

                if pos != 0:

                    raise ValueError("First position of 'curvatures' must be equal to zero!")

            if len(curvatures['values']) > 1 and ii == len(curvatures['values'])-1:

                if pos == self.track_data['stops']['values'][-1]:

                    raise ValueError("Last position of 'curvatures' must be smaller than the track length!")

            if ii > 0 and pos <= curvatures['values'][ii-1][0]:

                raise ValueError("Positions in 'curvatures' must be strictly increasing! Error at point {}.".format(ii+1))


    def validate_tunnels(self):

        if not 'tunnels' in self.track_data:

            return

        tunnels = self.track_data['tunnels']

        fields = {'units', 'values'}

        if fields != tunnels.keys():

            raise ValueError("Unexpected keys in 'tunnels'! Expecting 'units' and 'values'.")

        fields_units = {'position', 'length', 'cross section'}

        if fields_units != tunnels['units'].keys():

            raise ValueError("Unexpected keys in units of 'tunnels'! Expecting 'position', 'length' and 'cross section'.")

        if tunnels['units']['position'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in 'position' of 'tunnels'! Expecting 'm' or 'km'.")

        if tunnels['units']['length'] not in {'m', 'km'}:

            raise ValueError("Unexpected unit in 'length' of 'tunnels'! Expecting 'm' or 'km'.")

        if tunnels['units']['cross section'] not in {'m^2'}:

            raise ValueError("Unexpected unit in 'cross section' of 'tunnels'! Expecting 'm^2'.")

        for ii, v in enumerate(tunnels['values']):

            if len(v) != 3:

                raise ValueError("Unexpected size of nested list in 'tunnels'! Expecting 3, got {}.".format(len(v)))

            pos = v[0]

            if type(pos) not in {float, int}:

                raise ValueError("Unexpected value type in position of 'tunnels'! Expecting float or int, found {}.".format(type(pos)))

            try:

                length = float(v[1])

            except:

                raise ValueError("Unexpected value for 'length' in 'tunnels'! Expecting a finite positive number, got '{}' at position {}.".format(v[1], ii))

            if not math.isfinite(length) or length < 0:

                raise ValueError("Unexpected value for 'length' in 'tunnels'! Expecting a finite positive number, got '{}' at position {}.".format(v[1], ii))

            if pos + length > self.track_data['stops']['values'][-1]:

                raise ValueError("End of tunnel must be smaller than the track length!")

            try:

                cross_section = float(v[2])

            except:

                raise ValueError("Unexpected value for 'cross section' in 'tunnels'! Expecting a finite number, got {} at position {}.".format(v[2], ii))

            if not math.isfinite(cross_section) or cross_section < 0:

                raise ValueError("Unexpected value for 'cross section' in 'tunnels'! Expecting a finite number, got '{}' at position {}.".format(v[2], ii))

            if pos < 0:

                raise ValueError("Position of 'tunnels' must be positive!")

            if len(tunnels['values']) > 1 and ii == len(tunnels['values'])-1:

                if pos == self.track_data['stops']['values'][-1]:

                    raise ValueError("Last position of 'tunnels' must be smaller than the track length!")

            if ii > 0 and pos <= tunnels['values'][ii-1][0]:

                raise ValueError("Positions in 'tunnels' must be strictly increasing! Error at point {}.".format(ii+1))


    def validate_parameter_dict(self, key, parameter, units, strictly_positive=True, integer=False, upper_bound=None):

        fields = {'unit', 'value'}

        if fields != parameter.keys():

            raise ValueError("Unexpected keys in '{}'! Expecting 'unit' and 'value'.".format(key))

        if parameter['unit'] not in units:

            raise ValueError("Unexpected unit in '{}'!".format(key))

        value = parameter['value']

        if type(value) not in {float, int}:

            raise ValueError("Unexpected value type in '{}'! Expecting float or int, found {}.".format(key, type(value)))

        if integer and type(value) is not int:

            raise ValueError("Unexpected value type in '{}'! Expecting int, found {}.".format(key, type(value)))

        if not math.isfinite(value):

            raise ValueError("Value in '{}' must be finite!".format(key))

        if strictly_positive and value <= 0:

            raise ValueError("Value in '{}' must be strictly positive!".format(key))

        if not strictly_positive and value < 0:

            raise ValueError("Value in '{}' must be positive!".format(key))

        if upper_bound is not None:

            upper_bound = upper_bound[parameter['unit']] if isinstance(upper_bound, dict) else upper_bound

            if value > upper_bound:

                raise ValueError("Value in '{}' must be smaller than or equal to {}!".format(key, upper_bound))


    def validate_etcs_braking_data(self):

        if not 'ETCS braking data' in self.track_data:

            return

        etcs_data = self.track_data['ETCS braking data']

        fields = {'M_NVAVADH', 'Kt_int'}

        if fields != etcs_data.keys():

            missing = ", ".join([f"'{item}'" for item in fields - set(etcs_data)])
            redundant = ", ".join([f"'{item}'" for item in set(etcs_data) - fields])

            raise ValueError("Unexpected keys in 'ETCS braking data'! Missing: {}. Redundant: {}.".format(missing, redundant))

        self.validate_parameter_dict('M_NVAVADH', etcs_data['M_NVAVADH'], {'-'}, strictly_positive=False)
        self.validate_parameter_dict('Kt_int', etcs_data['Kt_int'], {'-'})


if __name__ == '__main__':

    validator = TrackValidator()

    tracks_dir = "../tracks"

    for file in os.listdir(tracks_dir):

        if file.endswith(".json"):

            id, _ = os.path.splitext(file)

            print("Validating track: {}".format(id))

            validator.validate_track(os.path.join(tracks_dir, file))

            print("ok")

