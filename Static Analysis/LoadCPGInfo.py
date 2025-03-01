import pandas as pd
import os
from collections import defaultdict, deque

NodesNames = [
    'FILE', 'METHOD', 'BLOCK', 'CALL', 'CALL_REPR', 'CONTROL_STRUCTURE',
    'EXPRESSION', 'FIELD_IDENTIFIER', 'IDENTIFIER', 'JUMP_LABEL',
    'JUMP_TARGET', 'LITERAL', 'LOCAL', 'METHOD_REF', 'MODIFIER', 'RETURN',
    'TYPE_REF', 'UNKNOWN'
]
EdgeNames = ['CDG', 'REACHING_DEF', 'CALL']


def load_Nodes_FIleHeader_Path(basePath):
    Header_files = []
    for name in NodesNames:
        fileName = 'nodes_' + name + '_header.csv'
        if os.path.exists(basePath + '/' + fileName):
            Header_files.append(basePath + '/' + fileName)
    return Header_files


def load_Nodes_FIle_Path(basePath):
    node_files = []
    for name in NodesNames:
        fileName = 'nodes_' + name + '_data.csv'
        if os.path.exists(basePath + '/' + fileName):
            node_files.append(basePath + '/' + fileName)
    return node_files


def load_Edge_FIle_Path(basePath):
    edge_files = {}
    for name in EdgeNames:
        fileName = 'edges_' + name + '_data.csv'
        if os.path.exists(basePath + '/' + fileName):
            edge_files[name] = basePath + '/' + fileName
    return edge_files


def load_graph_data(basePath):
    node_files, edge_files = load_Nodes_FIle_Path(basePath), load_Edge_FIle_Path(basePath)
    nodes = set()
    for file in node_files:
        df = pd.read_csv(file)
        nodes.update(df.iloc[:, 0].tolist())
    adjacency_list = {
        "CDG": defaultdict(list),
        "REACHING_DEF": defaultdict(list),
        "CALL": defaultdict(list)
    }
    for edge_type, file in edge_files.items():
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            start, end = row.iloc[0], row.iloc[1]
            adjacency_list[edge_type][end].append(start)
    return nodes, adjacency_list


def reverse_adjacency_list(adjacency_list):
    reversed_list = defaultdict(list)
    for end, start_list in adjacency_list.items():
        for start in start_list:
            reversed_list[start].append(end)
    return reversed_list


def get_line_numbers_for_nodes(node_ids, basePath):
    line_numbers = {}
    data_csv_paths, header_csv_paths = load_Nodes_FIle_Path(basePath), load_Nodes_FIleHeader_Path(basePath)
    for data_csv_path, header_csv_path in zip(data_csv_paths, header_csv_paths):
        with open(header_csv_path, 'r') as f:
            header_line = f.readline().strip()
            column_names = header_line.split(',')
        if 'LINE_NUMBER:int' not in column_names:
            continue
        line_number_index = column_names.index('LINE_NUMBER:int')
        data_df = pd.read_csv(data_csv_path, header=None, names=column_names)
        for node_id in node_ids:
            node_row = data_df[data_df.iloc[:, 0] == node_id]
            if not node_row.empty:
                line_number = node_row.iloc[0, line_number_index]
                line_numbers[node_id] = line_number
    return line_numbers


def get_filepath_for_node(node_ids, basePath):
    node_file = {}
    file_nodes_df = None
    method_nodes_df = None
    contain_edges_df = None
    file_node_ids = []
    method_nodes_ids = []
    contain_start = []
    contain_end = []
    File_node_file_path = basePath + '/nodes_FILE_data.csv'
    Method_node_file_path = basePath + '/nodes_METHOD_data.csv'
    Contain_edge_file_path = basePath + '/edges_CONTAINS_data.csv'
    if os.path.exists(File_node_file_path):
        file_nodes_df = pd.read_csv(File_node_file_path, header=None)
        file_node_ids = file_nodes_df.iloc[:, 0].values
    if os.path.exists(Method_node_file_path):
        method_nodes_df = pd.read_csv(Method_node_file_path, header=None)
        method_nodes_ids = method_nodes_df.iloc[:, 0].values
    if os.path.exists(Contain_edge_file_path):
        contain_edges_df = pd.read_csv(Contain_edge_file_path, header=None)
        contain_start = contain_edges_df.iloc[:, 0].values
        contain_end = contain_edges_df.iloc[:, 1].values
    if file_nodes_df is not None:
        for node_id in node_ids:
            if node_id in file_node_ids:
                node_row = file_nodes_df[file_nodes_df.iloc[:, 0] == node_id].iloc[0]
                node_file[node_id] = node_row.iloc[7]
    if method_nodes_df is not None:
        for node_id in node_ids:
            if node_id in method_nodes_ids:
                node_row = method_nodes_df[method_nodes_df.iloc[:, 0] == node_id].iloc[0]
                node_file[node_id] = node_row.iloc[7]
    if contain_edges_df is not None:
        for node_id in node_ids:
            if node_id in contain_end:
                indices = (contain_end == node_id)
                start_id = contain_start[indices][0]
                if file_nodes_df is not None and start_id in file_node_ids:
                    node_row = file_nodes_df[file_nodes_df.iloc[:, 0] == start_id].iloc[0]
                    node_file[node_id] = node_row.iloc[7]
                elif method_nodes_df is not None and start_id in method_nodes_ids:
                    node_row = method_nodes_df[method_nodes_df.iloc[:, 0] == start_id].iloc[0]
                    node_file[node_id] = node_row.iloc[7]
    return node_file


def is_method_id(id, base_path):
    method_csv = base_path + '/nodes_METHOD_data.csv'
    method_df = pd.read_csv(method_csv, header=None)
    return id in method_df.iloc[:, 0].values


def getContainMethodId(id, base_path):
    contains_csv = base_path + '/edges_CONTAINS_data.csv'
    contains_df = pd.read_csv(contains_csv, header=None)
    method_csv_path = base_path + '/nodes_METHOD_data.csv'
    method_df = pd.read_csv(method_csv_path, header=None)
    method_ids = set(method_df.iloc[:, 0].values)
    contain_rows = contains_df[contains_df.iloc[:, 1] == id]
    for _, row in contain_rows.iterrows():
        potential_method_id = row.iloc[0]
        if potential_method_id in method_ids:
            return potential_method_id
    return None
