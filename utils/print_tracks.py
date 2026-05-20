import os
import json
import numpy as np

def print_tracks(tracks_dir, filename=None):

    # TODO: check filename ends with csv

    rows = []

    rows += [[
        'ID',
        'Min speed limit [km/h]',
        'Max speed limit [km/h]',
        'Min gradient [permil]',
        'Max gradient [permil]',
        'Min (abs) radius [m]',
        'Length [m]',
        'Min interval [m]',
        'Max interval [m]',
        'Num intervals [-]',
        'Num stops [-]',
        'Num tunnels',
        'Min tunnel length [m]',
        'Max tunnel length [m]'
        ]]

    for file in os.listdir(tracks_dir):

        if file.endswith(".json"):

            with open(os.path.join(tracks_dir, file)) as f:

                data = json.load(f)

            id, _ = os.path.splitext(file)

            length = data['stops']['values'][-1]
            num_stops = len(data['stops']['values'])

            speed_limit_values = [v[1]*(3.6 if data['speed limits']['units']['velocity'] == 'm/s' else 1) for v in data['speed limits']['values']]  # km/h
            speed_limit_positions = [v[0]*(1e3 if data['speed limits']['units']['position'] == 'km' else 1) for v in data['speed limits']['values']]  # m

            if 'gradients' in data:

                gradient_values = [v[1] for v in data['gradients']['values']]  # permil
                gradient_positions = [v[0]*(1e3 if data['gradients']['units']['position'] == 'km' else 1) for v in data['gradients']['values']]  # m

            else:

                gradient_values, gradient_positions = [0.0], [0.0]

            if 'curvatures' in data:

                available_units = ['position', 'radius at start', 'radius at end']
                radius_values_non_negative = [abs(float(v[i]))*(1e3 if data['curvatures']['units'][available_units[i]] == 'km' else 1) for v in data['curvatures']['values'] for i in range(1,3) ] # m
                radius_positions = [v[0]*(1e3 if data['curvatures']['units']['position'] == 'km' else 1) for v in data['curvatures']['values']]  # m

            else:

                radius_values_non_negative, radius_positions = [float("infinity")], [0.0]

            positions = sorted(set(speed_limit_positions + gradient_positions + radius_positions + [length]))
            intervals = np.diff(positions)

            if not 'tunnels' in data:
                tunnel_lengths = None
            else:
                tunnel_lengths = [v[0]*(1e3 if data['tunnels']['units']['length'] == 'km' else 1) for v in data['tunnels']['values']]  # m

            rows += [[
                id,
                min(speed_limit_values),
                max(speed_limit_values),
                min(gradient_values),
                max(gradient_values),
                min(radius_values_non_negative),
                length,
                float(round(min(intervals), 1)),
                float(round(max(intervals), 1)),
                len(intervals),
                num_stops,
                len(tunnel_lengths) if tunnel_lengths is not None else 0,
                min(tunnel_lengths) if tunnel_lengths is not None else 0,
                max(tunnel_lengths) if tunnel_lengths is not None else 0
                ]]

    if filename is not None:

        content = ''

        for row in rows:

            row = [str(r) for r in row]
            content += ','.join(row)
            content += '\n'

        f = open(filename, 'w')
        f.write(content)
        f.close()

    else:

        for row in rows:

            print(row)  # TODO: nicer print


if __name__ == '__main__':

    tracks_dir = "../tracks"

    print_tracks(tracks_dir, filename=None)
