#!/usr/bin/env python3

import colorbrewer as cb
import pandas as pd
import numpy as np
import random
from itolparser.version import __version__, __author__, __description__
import bisect

import logging

from itolparser.args import get_args, validate_args, select_input_type


# SAMPLE IDS NEED TO END UP IN DATA ALONGSIDE VALUES
class Itolparser:
    def __init__(
        self,
        input=None,
        delim=None,
        outdir=None,
        ignore_cols=None,
        continuous_cols=None,
        margin=None,
        stripwidth=None,
        maxcategories=None,
        df=None,
    ):
        self.input = input
        self.delim = delim
        self.outdir = outdir
        self.ignore_cols = ignore_cols
        self.continuous_cols = continuous_cols
        self.margin = margin
        self.stripwidth = stripwidth
        self.maxcategories = maxcategories
        self.df = df

    def read_input(self):
        """Read in typing/metadata table using the provided delimiter"""
        self.df = pd.read_csv(self.input, sep=self.delim)

    # def make_output_dir(self):
    #     """Make output directory if it does not exist yet"""
    #     self.outdir.mkdir(parents=True, exist_ok=True)

    def build_settings_dict(self, data_cols):
        # Initialize dictionary with column names
        settings_dict = {}
        if self.ignore_cols is None:
            self.ignore_cols = []
        if self.continuous_cols is None:
            self.continuous_cols = []
        for name in data_cols:
            if name not in self.ignore_cols:
                if name in self.continuous_cols:
                    # Setting a nested dict so that other column-specific attributes can be added later
                    settings_dict[name] = {"continuous": True}
                    logging.info(f"Treating column {name} as continuous")
                else:
                    settings_dict[name] = {"continuous": False}
            else:
                logging.info(f"Ignoring column {name}")
        return settings_dict


class ItolparserColumn:
    def __init__(self, name, margin, stripwidth, column_data, outdir):
        self.name = name
        self.margin = margin
        self.stripwidth = stripwidth
        self.outdir = outdir
        self.colordict = None
        self.printname = "".join(i for i in name if i not in r'\/:*?"<>|')
        self.label_string = None
        self.color_string = None
        self.shape_string = None
        self.legend_text = None
        self.column_data = column_data
        self.list_removevals = [
            "none",
            "absent",
            "nan",
            "na",
            "-",
        ]

    def get_unique_values(self, df):
        """Get unique values from the column"""
        list_unique_values = list(df.iloc[:, 1].unique())
        return list_unique_values

    def remove_na_values(self, list_unique_values, list_removevals):
        for unique_value in list_unique_values:
            if str(unique_value).lower() in list_removevals:
                list_unique_values.remove(unique_value)
            elif unique_value in list_removevals:
                list_unique_values.remove(unique_value)

        return list_unique_values

    def rgb_to_hex(self, rgb_tuple):
        return f"#{rgb_tuple[0]:02x}{rgb_tuple[1]:02x}{rgb_tuple[2]:02x}"

    def make_legend_text(self, printname, colordict):
        """Make legend text for the current column"""
        label_string = ",".join([str(x) for x in colordict.keys()])
        color_string = ",".join([str(x) for x in colordict.values()])
        shape_string = ",".join(["1"] * len(colordict))

        legend_text = []
        legend_text.append("DATASET_COLORSTRIP")
        legend_text.append("SEPARATOR COMMA")
        legend_text.append("BORDER_WIDTH,0.5")
        legend_text.append("COLOR,#000000")
        legend_text.append(f"DATASET_LABEL,{printname}")
        legend_text.append(f"LEGEND_COLORS,{color_string},#ffffff")
        legend_text.append(f"LEGEND_LABELS,{label_string},NA")
        legend_text.append(f"LEGEND_SHAPES,{shape_string},1")
        legend_text.append(f"LEGEND_TITLE,{printname}")
        legend_text.append(f"MARGIN,{self.margin}")
        legend_text.append(f"STRIP_WIDTH,{self.stripwidth}")
        legend_text.append("DATA\n")
        legend_text = "\n".join(legend_text)

        return legend_text

    def write_file(self, outdir, printname, legend_text, data_text):
        outdir.mkdir(parents=True, exist_ok=True)
        filename = f"DATASET_COLORSTRIP_{printname}.txt"
        filepath = outdir / filename
        with open(filepath, "w") as f:
            f.write(legend_text)
            f.write(data_text)


class ItolparserDiscreteColumn(ItolparserColumn):
    def __init__(self, name, margin, stripwidth, column_data, outdir):
        super().__init__(name, margin, stripwidth, column_data, outdir)

    def select_color_palette(self, list_unique_values):
        """
        Returns a color palette in RGB values based on the number of unique values in the column
        """
        nr_unique_values = len(list_unique_values)
        if nr_unique_values == 1:
            color_palette = (0, 0, 0)
        elif nr_unique_values <= 2:
            color_palette = [(189, 189, 189), (240, 59, 32)]
        elif nr_unique_values <= 12:
            color_palette = cb.Paired[nr_unique_values]
        elif nr_unique_values <= 18:
            color_palette = cb.Set1[9] + cb.Pastel1[nr_unique_values - 9]
        else:
            # Generate random RGB values for each unique value
            color_palette = [
                tuple([random.randint(0, 255) for i in range(3)])
                for j in range(nr_unique_values)
            ]

        return color_palette

    def build_colordict(self, list_unique_values, color_palette):
        """Process a column of the input table"""
        colordict = {}
        if len(list_unique_values) == 1:
            colordict[list_unique_values[0]] = self.rgb_to_hex(color_palette)
        else:
            for val in list_unique_values:
                val_index = list_unique_values.index(val)
                rgb_val = color_palette[val_index]
                HEX = self.rgb_to_hex(rgb_val)
                colordict[val] = HEX
        return colordict

    def make_data_section(self, column_data, colordict):
        # map colordict to second column of column_data
        color_data = column_data.iloc[:, 1].map(colordict)
        df_data = pd.concat(
            [column_data.iloc[:, 0], color_data, column_data.iloc[:, 1]], axis=1
        )
        data_text = df_data.to_csv(sep=",", header=False, index=False)

        return data_text

    def process_column(self):
        # Get unique values and remove specified items
        self.list_unique_values = self.get_unique_values(self.column_data)
        self.list_unique_values = self.remove_na_values(
            self.list_unique_values, self.list_removevals
        )
        self.color_palette = self.select_color_palette(self.list_unique_values)
        self.colordict = self.build_colordict(
            self.list_unique_values, self.color_palette
        )
        self.legend_text = self.make_legend_text(self.printname, self.colordict)
        self.data_text = self.make_data_section(self.column_data, self.colordict)
        self.write_file(self.outdir, self.printname, self.legend_text, self.data_text)


class ItolparserContinuousColumn(ItolparserColumn):
    def __init__(self, name, margin, stripwidth, column_data, outdir, palette_name):
        super().__init__(name, margin, stripwidth, column_data, outdir)
        self.palette_name = palette_name
        self.color_palette = None

    def build_colordict(self, list_unique_values, palette_name):
        color_palette = getattr(cb, palette_name)[5]
        min_val = min(list_unique_values)
        max_val = max(list_unique_values)
        range_vals = max_val - min_val

        legend_values = np.arange(
            min_val,
            max_val + range_vals / len(color_palette),
            range_vals / (len(color_palette) - 1),
        )
        legend_values = [round(i, 1) for i in legend_values]

        color_dict = {}
        for index, val in enumerate(legend_values):
            color_dict[str(val)] = self.rgb_to_hex(color_palette[index])

        return color_dict, color_palette

    def get_medium_rgb_value(self, rgb_left, rgb_right, ratio):
        rgb_new = [0, 0, 0]
        for i in range(3):
            rgb_new[i] = round(rgb_left[i] + (rgb_right[i] - rgb_left[i]) * ratio)
        return tuple(rgb_new)

    def get_hex_color(self, val, color_dict, color_palette):
        val_list = [float(val) for val in color_dict.keys()]
        if float(val) in val_list:
            final_hex_val = color_dict[str(float(val))]
        else:
            right_index = bisect.bisect(val_list, val)
            left_index = right_index - 1
            left_rgb = color_palette[left_index]
            right_rgb = color_palette[right_index]
            ratio = (val - val_list[left_index]) / (
                val_list[right_index] - val_list[left_index]
            )
            final_rgb_val = self.get_medium_rgb_value(left_rgb, right_rgb, ratio)
            final_hex_val = self.rgb_to_hex(final_rgb_val)
        return final_hex_val

    def make_data_section(self, column_data, colordict, color_palette):
        color_data = pd.Series(0, index=np.arange(column_data.shape[0]))
        for index, row in column_data.iterrows():
            # if row[self.name] == 0:
            #     color_data[index] = "#ffffff"
            # else:
            color_data[index] = self.get_hex_color(
                row[self.name], colordict, color_palette
            )
        df_data = pd.concat(
            [column_data.iloc[:, 0], color_data, column_data.iloc[:, 1]], axis=1
        )
        data_text = df_data.to_csv(sep=",", header=False, index=False)
        return data_text

    def process_column(self):
        self.list_unique_values = self.get_unique_values(self.column_data)
        self.list_unique_values = self.remove_na_values(
            self.list_unique_values, self.list_removevals
        )
        self.colordict, self.color_palette = self.build_colordict(
            self.list_unique_values, self.palette_name
        )
        self.legend_text = self.make_legend_text(self.printname, self.colordict)
        self.data_text = self.make_data_section(
            self.column_data,
            self.colordict,
            self.color_palette,
        )
        self.write_file(self.outdir, self.printname, self.legend_text, self.data_text)


def main():
    args = get_args()
    validate_args(args)
    delim = select_input_type(args)

    sample = Itolparser(
        input=args.input,
        delim=delim,
        outdir=args.outdir,
        ignore_cols=args.ignore,
        continuous_cols=args.continuous,
        margin=args.margin,
        stripwidth=args.stripwidth,
        maxcategories=args.maxcategories,
    )

    # Read in typing/metadata table using the provided delimiter
    sample.read_input()

    # Get column name of samples
    id_name = sample.df.columns[0]

    data_cols = sample.df.columns[1:]

    settings_dict = sample.build_settings_dict(data_cols)

    # Loop over columns
    for name in data_cols:
        if name not in settings_dict:
            logging.info(f"Skipping column {name}")
            continue

        column_data = sample.df[[id_name, name]]

        if settings_dict[name]["continuous"]:
            column_object = ItolparserContinuousColumn(
                name=name,
                margin=sample.margin,
                stripwidth=sample.stripwidth,
                column_data=column_data,
                outdir=sample.outdir,
                palette_name=args.palette,
            )
            column_object.process_column()
        else:
            column_object = ItolparserDiscreteColumn(
                name=name,
                margin=sample.margin,
                stripwidth=sample.stripwidth,
                column_data=column_data,
                outdir=sample.outdir,
            )
            column_object.process_column()
