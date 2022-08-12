#!/usr/bin/python3

import os, sys
import shutil
import pandas as pd
import numpy as np
import re
import json
import argparse

__version__ = '1.0.0'

parser = argparse.ArgumentParser(description='Getting overrepresented sequences (part 1)')
parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
parser.add_argument('--input-path-to-fastqc-files', '-i', metavar='input_path_to_fastqc_files', type=str, required=True, help='path to fastqc files')
parser.add_argument('--output-file-path', '-o', metavar='output_file_path', type=str, required=True, help='output file path')
args = parser.parse_args()


def parse_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    start_line = 0
    edges = []

    # looking for boundaries of table with info, by splitting .txt file by "END_MODULE"
    for line_num, line in enumerate(lines):
        if line.find("END_MODULE") != -1:
            edges.append([start_line, line_num])
            start_line = line_num + 1

    file_dict = {}
    file_names = []
    col_names = []

    # filling in dictionary {filename(string): table with info(array2d)}
    for edge in edges[:11]:
        if (edge[1] - edge[0]) <= 1:
            continue

        SDP_info = None
        # first element of first line contains the name of table
        filename = lines[edge[0]].split('\t')[0]
        filename = re.sub('>>', '', filename)
        file_names.append(filename)

        table = []

        # SDL stats
        if filename == 'Sequence Duplication Levels':
            SDP_info = float(((lines[edge[0] + 1].split('\t'))[-1])[:-1])
            edge[0] += 1

        for line in lines[edge[0] + 1:edge[1]]:
            # deleting '\n' symbol
            line = line[:-1]
            table.append(line.split('\t'))

        col_names.append(table.pop(0))
        file_dict[filename] = table

    # deliting first table, which don't contain any info
    col_names.pop(0)
    file_names.pop(0)

    return file_names, file_dict, col_names, SDP_info


def create_dataframes(file_names, file_dict, col_names, sample_name):
    """
    Args:
    - file_names - list of table names in fastqc_data.txt
    - file_dict - dictionary key:tablename -> value:table content
    - col_names - list of arrays(names of columnes) to create dataframes

    """

    for cnt, file_name in enumerate(file_names):
        data = file_dict[file_name]
        columns = col_names[cnt]

        df = pd.DataFrame(data, columns=columns)

        indexes = df.filter(regex="^#").columns[0]
        df = df.set_index(indexes)

        path = os.path.join(args.output_file_path + sample_name, file_name + '.pkl')

        with open(path, 'wb') as csvfile:
            df.to_pickle(path)

def main():

    os.mkdir(args.output_file_path)
    files_fastqc = os.listdir(args.input_path_to_fastqc_files)
    for file in files_fastqc:
        file_names, file_dict, col_names, SDP_info = parse_data(os.path.join(args.input_path_to_fastqc_files, file))
        os.mkdir(args.output_file_path + file[:-4])
        create_dataframes(file_names, file_dict, col_names, file[:-4])
    
if __name__ == "__main__": main()

