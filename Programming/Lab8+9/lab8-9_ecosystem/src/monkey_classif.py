import argparse
import collections

import pandas
import pandas as pd
import utils
import monkey_model
from operator import itemgetter
from utils import check_hexacolor
from utils import euclidean_distance
from utils import get_cli_args
import numpy as np

from monkey_model import Monkey
from utils import check_hexacolor, hexacolor_to_int, euclidean_distance, get_cli_args, VALID_OBS, patch_color_int


def read_monkeys_from_csv(csv_filepath: str, strict: bool = False) -> pd.DataFrame:
    """Read a monkey data from a CSV file and produce and return a dataframe"""
    df = pd.read_csv(csv_filepath)

    if list(df.columns.values) != ['species', 'size', 'weight', 'color']:
        return ValueError

    df['monkey'] = ''
    df['bmi'] = 0.0
    df['fur_color_int'] = 0

    for i in range(len(df)):

        if (df['size'][i] <= 0) or (df['weight'][i] <= 0) or (not (utils.check_hexacolor(str(df['color'][i])))):

            df = df.drop([i])

        else:

            monkey = monkey_model.Monkey(df['color'][i], df['size'][i], df['weight'][i], df['species'][i])
            df['monkey'][i] = monkey
            df['bmi'][i] = monkey.compute_bmi()
            df['fur_color_int'][i] = int('0x' + monkey.fur_color[1:], 16)

    df = df.dropna()
    return df


path = 'Programming/Lab8+9/lab8-9_ecosystem/data/monkeys.csv'
df = read_monkeys_from_csv(path)
print(df['monkey'][1].size)


def compute_knn(df: pd.DataFrame, k: int = 5, columns: list = ["fur_color_int", "bmi"]) -> pd.DataFrame:
    """update species information for a Monkey DataFrame using a KNN.
    Arguments:
        `df`: dataframe as obtained from `read_monkeys_from_csv`
        `k`: number of neighbors to consider
        `columns`: list of observations to consider. Are valid observations:
            - fur_color_int,
            - fur_color_int_r (for red hue of fur),
            - fur_color_int_g (for green hue of fur),
            - fur_color_int_b (for blue hue of fur),
            - weight
            - size
            - bmi
    Returns: the dataframe `df`, modified in-place
    """

    """KNN classification algorithm to retrieve
        the species attribute of Monkey objects whenever it is missing."""

    print("KNN computation running...\nEstimated runtime: 1min 20sec.")

    for index1, row1 in pd.DataFrame.iterrows():  # for each unlabelled item
        if row1[8] == "yes":
            my_dict = {}  # create a dict
            for index2, row2 in pd.DataFrame.iterrows():  # for each labelled item
                if row2[8] == "no":
                    # fill the dict with {labelled item: distance to unlabelled item} pairs
                    my_dict[row2[0]] = euclidean_distance(row1[7], row1[6], row2[7], row2[6])

            # list of k tuples (index of labelled item, distance to unlabelled item)
            # which are the closest to the unlabelled item
            k_closest = sorted(my_dict.items(), key=itemgetter(1))[:k]

            # retrieve from the dataframe the names of the k species listed in k_closest
            close_species = []
            for i in k_closest:
                close_species.append(pd.DataFrame.loc[pd.DataFrame["id"] == i[0], "species"].iloc[0])

            # compute the most frequent species name in close_species
            closest_species = max(set(close_species), key=close_species.count)

            # update the dataframe and replace the empty string by the closest species
            pd.DataFrame.loc[pd.DataFrame.id == row1[0], "species"] = closest_species

    return pd.DataFrame


def save_to_csv(dataframe: pd.DataFrame, csv_filename: str):
    """Save monkey dataframe to CSV file"""
    dataframe.drop(columns=["monkey", "fur_color_int", "bmi"]).to_csv(csv_filename, index=False)


def main():
    args = get_cli_args()
    if args.command == "knn":
        df = read_monkeys_from_csv(args.input_csv)
        df = compute_knn(df, k=args.k, columns=args.obs)
        save_to_csv(df, args.output_csv)
    elif args.command == "visualize":
        from monkey_visualize import scatter
        scatter(args.input_csv, args.obs_a, args.obs_b)
    else:
        # this should be dead code.
        raise RuntimeError("invalid command name")


# main entry point
if __name__ == "__main__":
    main()
