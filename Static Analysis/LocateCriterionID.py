import ast
import pandas as pd
from LoadCPGInfo import load_Nodes_FIle_Path, load_Nodes_FIleHeader_Path


def get_function_name_from_ast(basePath, file_path, line_number):
    is_method = False
    with open(basePath + '/' + file_path, "r", encoding="utf-8", errors="ignore") as file:
        tree = ast.parse(file.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                if node.lineno == line_number:
                    is_method = True
                    return is_method, node.name, node.lineno
                if node.lineno < line_number <= node.end_lineno:
                    return is_method, node.name, node.lineno
    return is_method, None, None


def get_function_id_from_candidate_id(contain_df, canditate_ids):
    line_method_ids_map = {}
    for canditate_id in canditate_ids:
        method_ids = []
        matching_rows = contain_df[contain_df.iloc[:, 1] == canditate_id]
        if not matching_rows.empty:
            method_ids.append(matching_rows.iloc[0, 0])
        line_method_ids_map[canditate_id] = method_ids
    return line_method_ids_map


def find_correct_line_id_in_Method(line_method_ids_map, function_nodes_df, file_path, function_start_line, function_name):
    correctIds = []
    for lineID, method_ids in line_method_ids_map.items():
        for method_id in method_ids:
            method_row = function_nodes_df[function_nodes_df.iloc[:, 0] == method_id]
            if not method_row.empty:
                if ((method_row.iloc[:, 7] == file_path) &
                    (method_row.iloc[:, 11].astype(int) == function_start_line) &
                    (method_row.iloc[:, 13] == function_name)).all():
                    correctIds.append(lineID)
                    break
    return correctIds


def find_correct_line_id_in_File(line_file_ids_map, file_nodes_df, file_path):
    correctIds = []
    for lineID, file_ids in line_file_ids_map.items():
        for file_id in file_ids:
            file_row = file_nodes_df[file_nodes_df.iloc[:, 0] == file_id]
            if not file_row.empty:
                if (file_nodes_df.iloc[:, 7] == file_path):
                    correctIds.append(lineID)
                    break
    return correctIds


def get_node_id_for_line(file_path, line_number, Csv_basePath, source_code_basePath):
    canditate_ids = []
    correctIds = None
    function_nodes_path = Csv_basePath + '/nodes_METHOD_data.csv'
    file_nodes_path = Csv_basePath + '/nodes_FILE_data.csv'
    contain_edge_path = Csv_basePath + '/edges_CONTAINS_data.csv'

    contain_edges_df = pd.read_csv(contain_edge_path, header=None)
    function_nodes_df = pd.read_csv(function_nodes_path, header=None)
    file_nodes_df = pd.read_csv(file_nodes_path, header=None)

    is_function, function_name, function_start_line = get_function_name_from_ast(
        source_code_basePath, file_path, line_number
    )

    if is_function:
        matching_rows = function_nodes_df[
            (function_nodes_df.iloc[:, 7] == file_path) &
            (function_nodes_df.iloc[:, 11] == function_start_line) &
            (function_nodes_df.iloc[:, 13] == function_name)
        ]
        first_column_values = matching_rows.iloc[:, 0].tolist()
        return first_column_values

    NodesFilePaths = load_Nodes_FIle_Path(Csv_basePath)
    NodesFileHeaderPaths = load_Nodes_FIleHeader_Path(Csv_basePath)

    for data_csv_path, header_csv_path in zip(NodesFilePaths, NodesFileHeaderPaths):
        with open(header_csv_path, 'r', encoding="utf-8", errors="ignore") as f:
            header_line = f.readline().strip()
            column_names = header_line.split(',')
        if 'LINE_NUMBER:int' not in column_names:
            continue
        line_number_index = column_names.index('LINE_NUMBER:int')
        data_df = pd.read_csv(data_csv_path, header=None)
        matching_rows = data_df[data_df.iloc[:, line_number_index] == line_number]
        canditate_ids.extend(matching_rows.iloc[:, 0].tolist())

    line_method_ids_map = get_function_id_from_candidate_id(contain_edges_df, canditate_ids)

    if function_name:
        correctIds = find_correct_line_id_in_Method(
            line_method_ids_map, function_nodes_df, file_path, function_start_line, function_name
        )
    else:
        if len(line_method_ids_map) > 0:
            correctIds = find_correct_line_id_in_File(line_method_ids_map, file_nodes_df, file_path)

    return correctIds
