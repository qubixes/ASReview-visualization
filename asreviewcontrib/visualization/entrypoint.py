# Copyright 2020 The ASReview Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

from asreview.config import LOGGER_EXTENSIONS
from asreview.entry_points import BaseEntryPoint

from asreviewcontrib.visualization import Plot
from asreviewcontrib.visualization.quick import progression_plot
from asreviewcontrib.visualization.quick import inclusion_plot
import logging

PLOT_TYPES = ['inclusion', 'discovery', 'limits', 'progression']


class PlotEntryPoint(BaseEntryPoint):
    description = "Plotting functionality for logging files produced by "\
        "ASReview."
    extension_name = "asreview-visualization"

    def __init__(self):
        from asreviewcontrib.visualization.__init__ import __version__
        super(PlotEntryPoint, self).__init__()

        self.version = __version__

    def execute(self, argv):
        parser = _parse_arguments()
        args_dict = vars(parser.parse_args(argv))

        if args_dict['type'] == 'all':
            types = PLOT_TYPES
        else:
            arg_types = args_dict['type'].split(',')
            types = []
            for plot_type in arg_types:
                if plot_type not in PLOT_TYPES:
                    logging.warning(f'Plotting type "{plot_type} unknown."')
                else:
                    types.append(plot_type)

        if args_dict["absolute_format"]:
            result_format = "number"
        else:
            result_format = "percentage"

        prefix = args_dict["prefix"]
        with Plot.from_paths(args_dict["data_dirs"], prefix=prefix) as plot:
            if len(plot.analyses) == 0:
                print(f"No log files found in {args_dict['data_dirs']}.\n"
                      f"To be detected log files have to start with '{prefix}'"
                      f" and end with one of the following: \n"
                      f"{', '.join(LOGGER_EXTENSIONS)}.")
                return
            if "inclusion" in types:
                inclusion_plot(plot, result_format=result_format)
            if "discovery" in types:
                plot.plot_time_to_discovery(result_format=result_format)
            if "limits" in types:
                plot.plot_limits(result_format=result_format)
            if "progression" in types:
                progression_plot(plot, result_format=result_format)


def _parse_arguments():
    parser = argparse.ArgumentParser(prog='asreview plot')
    parser.add_argument(
        'data_dirs',
        metavar='N',
        type=str,
        nargs='+',
        help='Data directories.'
    )
    parser.add_argument(
        "-t", "--type",
        type=str,
        default="all",
        help="Type of plot to make. Separate by commas (no spaces) for"
        " multiple plots."
    )
    parser.add_argument(
        "-a", "--absolute-values",
        dest="absolute_format",
        action='store_true',
        help='Use absolute values on the axis instead of percentages.'
    )
    parser.add_argument(
        "--prefix",
        default="",
        help='Filter files in the data directory to only contain files'
             'starting with a prefix.'
    )
    return parser
