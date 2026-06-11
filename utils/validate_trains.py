import math
import os

import json


class TrainValidator():

    def __init__(self):

        self.required_fields = {
            'metadata',
            'mass',
            'rho',
            'max speed',
            'max traction power',
            'max reg braking power',
            'max traction force',
            'max reg braking force',
            'rolling resistance r0',
            'rolling resistance r1',
            'rolling resistance r2'
        }

        self.optional_fields = {
            'num seats',
            'num coaches',
            'length',
            'max pn braking force',
            'max acceleration',
            'max deceleration',
            'efficiency traction',
            'efficiency reg brake',
            'tunnel resistance',
            'ETCS braking data'
        }

        self.required_metadata = {'id', 'library version'}

        self.optional_metadata = {'description', 'created by', 'license'}

        self.train_data = None


    def validate_train(self, filename):

        self.load_json(filename)

        self.validate_keys()

        self.validate_metadata()

        self.validate_parameters()

        self.validate_efficiencies()

        self.validate_tunnel_resistance()

        self.validate_etcs_braking_data()


    def load_json(self, filename):

        try:

            with open(filename) as file:

                data = json.load(file)

        except FileNotFoundError:

            raise FileNotFoundError("Specified train file not found!")

        self.train_data = data
        self.filename = filename


    def validate_keys(self):
        "Check that all required keys are there and that there are no redundant fields."

        data = self.train_data

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

        metadata = self.train_data['metadata']

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

        train_ID, _ = os.path.splitext(self.filename.split(os.path.sep)[-1])

        if train_ID != metadata['id']:

            raise ValueError("Inconsistent ID between filename and metadata!")


    def validate_parameters(self):

        self.validate_parameter('num seats', {'-'}, integer=True)
        self.validate_parameter('num coaches', {'-'}, integer=True)

        self.validate_parameter('length', {'m', 'km'})
        self.validate_parameter('mass', {'kg', 't'})
        self.validate_parameter('rho', {'-', '%'}, strictly_positive=False)

        self.validate_parameter('max speed', {'m/s', 'km/h'})

        self.validate_parameter('max traction power', {'W', 'kW', 'MW'})
        self.validate_parameter('max reg braking power', {'W', 'kW', 'MW'})
        self.validate_parameter('max traction force', {'N', 'kN'})
        self.validate_parameter('max reg braking force', {'N', 'kN'})
        self.validate_parameter('max pn braking force', {'N', 'kN'}, strictly_positive=False)

        self.validate_parameter('max acceleration', {'m/s^2'})
        self.validate_parameter('max deceleration', {'m/s^2'})

        self.validate_parameter('rolling resistance r0', {'N', 'kN'})
        self.validate_parameter('rolling resistance r1', {'N/(m/s)', 'kN/(m/s)', 'kN/(km/h)'}, strictly_positive=False)
        self.validate_parameter('rolling resistance r2', {'N/(m/s)^2', 'kN/(m/s)^2', 'kN/(km/h)^2'})


    def validate_parameter(self, key, units, strictly_positive=True, integer=False, upper_bound=None):

        if key not in self.train_data:

            return

        self.validate_parameter_dict(key, self.train_data[key], units, strictly_positive, integer, upper_bound)


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


    def validate_efficiencies(self):

        if 'efficiency traction' in self.train_data or 'efficiency reg brake' in self.train_data:

            if 'efficiency traction' not in self.train_data or 'efficiency reg brake' not in self.train_data:

                raise ValueError("Both efficiencies need to be specified in json file!")

            self.validate_parameter('efficiency traction', {'-', '%'}, upper_bound={'-': 1, '%': 100})
            self.validate_parameter('efficiency reg brake', {'-', '%'}, upper_bound={'-': 1, '%': 100})


    def validate_tunnel_resistance(self):

        if not 'tunnel resistance' in self.train_data:

            return

        tunnel_resistance = self.train_data['tunnel resistance']

        fields = {'units', 'values'}

        if fields != tunnel_resistance.keys():

            raise ValueError("Unexpected keys in 'tunnel resistance'! Expecting 'units' and 'values'.")

        fields_units = {'cross section', 'coefficient'}

        if fields_units != tunnel_resistance['units'].keys():

            raise ValueError("Unexpected keys in units of 'tunnel resistance'! Expecting 'cross section' and 'coefficient'.")

        cross_section_units = {'m^2'}
        coefficient_units = {'N/(m/s)^2', 'kN/(km/h)^2', 'kg/m'}

        if tunnel_resistance['units']['cross section'] not in cross_section_units:

            raise ValueError("Unexpected unit in cross section of 'tunnel resistance'! Expecting 'm^2'.")

        if tunnel_resistance['units']['coefficient'] not in coefficient_units:

            raise ValueError("Unexpected unit in coefficient of 'tunnel resistance'!")

        for ii, v in enumerate(tunnel_resistance['values']):

            if len(v) != 2:

                raise ValueError("Unexpected size of nested list in 'tunnel resistance'! Expecting 2, got {}.".format(len(v)))

            cross_section, coefficient = v

            self.validate_parameter_dict('cross section',{'unit': tunnel_resistance['units']['cross section'], 'value': cross_section}, cross_section_units)
            self.validate_parameter_dict('coefficient',{'unit': tunnel_resistance['units']['coefficient'], 'value': coefficient}, coefficient_units)


    def validate_etcs_braking_data(self):

        if not 'ETCS braking data' in self.train_data:

            return

        etcs_data = self.train_data['ETCS braking data']

        fields = {
            'A_brake_emergency',
            'A_brake_service',
            'K_dry_rst',
            'K_wet_rst',
            'T_traction',
            'T_be',
            'T_bs',
            'v_uncertainty'
        }

        if fields != etcs_data.keys():

            missing = ", ".join([f"'{item}'" for item in fields-set(etcs_data)])
            redundant = ", ".join([f"'{item}'" for item in set(etcs_data)-fields])

            raise ValueError("Unexpected keys in 'ETCS braking data'! Missing: {}. Redundant: {}.".format(missing, redundant))

        self.validate_braking_curve('A_brake_emergency')
        self.validate_braking_curve('A_brake_service')

        self.validate_parameter_dict('K_dry_rst', etcs_data['K_dry_rst'], {'-'})
        self.validate_parameter_dict('K_wet_rst', etcs_data['K_wet_rst'], {'-'})
        self.validate_parameter_dict('T_traction', etcs_data['T_traction'], {'s'})
        self.validate_parameter_dict('T_be', etcs_data['T_be'], {'s'})
        self.validate_parameter_dict('T_bs', etcs_data['T_bs'], {'s'})
        self.validate_parameter_dict('v_uncertainty', etcs_data['v_uncertainty'], {'-', '%'}, strictly_positive=False, upper_bound={'-': 1, '%': 100})

    def validate_braking_curve(self, key):

        braking_curve = self.train_data['ETCS braking data'][key]

        fields = {'units', 'values'}

        if fields != braking_curve.keys():

            raise ValueError("Unexpected keys in '{}'! Expecting 'units' and 'values'.".format(key))

        fields_units = {'velocity', 'deceleration'}

        if fields_units != braking_curve['units'].keys():

            raise ValueError("Unexpected keys in units of '{}'! Expecting 'velocity' and 'deceleration'.".format(key))

        velocity_units = {'m/s', 'km/h'}
        deceleration_units = {'m/s^2'}

        if braking_curve['units']['velocity'] not in velocity_units:

            raise ValueError("Unexpected unit in velocity of '{}'! Expecting 'm/s' or 'km/h'.".format(key))

        if braking_curve['units']['deceleration'] not in deceleration_units:

            raise ValueError("Unexpected unit in deceleration of '{}'! Expecting 'm/s^2'.".format(key))

        if len(braking_curve['values']) == 0:

            raise ValueError("'{}' must contain at least one value!".format(key))

        for ii, v in enumerate(braking_curve['values']):

            if len(v) != 2:

                raise ValueError("Unexpected size of nested list in '{}'! Expecting 2, got {}.".format(key, len(v)))

            velocity, deceleration = v

            self.validate_parameter_dict('velocity',{'unit': braking_curve['units']['velocity'], 'value': velocity}, velocity_units, strictly_positive=False)

            self.validate_parameter_dict('deceleration',{'unit': braking_curve['units']['deceleration'], 'value': deceleration}, deceleration_units)

            if ii > 0 and velocity <= braking_curve['values'][ii - 1][0]:

                raise ValueError("Velocities in '{}' must be strictly increasing! Error at point {}.".format(key, ii + 1))


if __name__ == '__main__':

    validator = TrainValidator()

    trains_dir = "../trains"

    for file in os.listdir(trains_dir):

        if file.endswith(".json"):

            id, _ = os.path.splitext(file)

            print("Validating train: {}".format(id))

            validator.validate_train(os.path.join(trains_dir, file))

            print("ok")