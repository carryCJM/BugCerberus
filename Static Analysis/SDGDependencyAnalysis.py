

import pandas as pd
from collections import defaultdict
from LoadSDGInfo import (load_graph_data,
                         reverse_adjacency_list,
                         get_line_numbers_for_nodes,
                         get_filepath_for_node,
                         is_method_id,
                         getContainMethodId)
from LocateCriterionID import get_node_id_for_line
from GetSliceContent import get_Pos_content



def find_Intra_path_to_node(start_node, adjacency_list, visited):
    if start_node in visited:
        return set()

    visited.add(start_node)
    reachable_nodes = set()


    for edge_type in ["CDG", "REACHING_DEF"]:
        if start_node in adjacency_list[edge_type]:
            for prev_node in adjacency_list[edge_type][start_node]:
                if prev_node not in visited:
                    reachable_nodes.add(prev_node)

                    reachable_nodes.update(find_Intra_path_to_node(prev_node, adjacency_list, visited))

    visited.remove(start_node)
    return reachable_nodes


def find_all_reachable_nodes_with_depth(start_node, adjacency_list, max_depth, depth=0, visited=None):

    if visited is None:
        visited = set()

    if start_node in visited:
        return set()

    if depth >= max_depth:
        return set()

    visited.add(start_node)
    reachable_nodes = set()


    for edge_type in ["CDG", "REACHING_DEF"]:
        if start_node in adjacency_list[edge_type]:
            next_nodes = adjacency_list[edge_type][start_node]
            for next_node in next_nodes:
                if next_node not in visited:
                    reachable_nodes.add(next_node)
                    reachable_nodes.update(
                        find_all_reachable_nodes_with_depth(
                            next_node, adjacency_list, max_depth, depth + 1, visited
                        )
                    )
    visited.remove(start_node)

    return reachable_nodes

def backward_traverse(start_node, adjacency_list, reversed_adjacency_CDGAndReaching, reversed_adjacency_CALL):
    results = []

    visited = set()  # 初始化访问集合
    Intra_results = find_Intra_path_to_node(start_node, adjacency_list, visited)
    Intra_results.add(start_node)  # 本身放进去
    callee_results = set()

    for start_node in reversed_adjacency_CALL.keys():
        if start_node in Intra_results:
            callee_nodes = reversed_adjacency_CALL[start_node]
            callee_results.update(callee_nodes)
            for callee_node in callee_nodes:
                reachable_nodes = find_all_reachable_nodes_with_depth(
                    callee_node, reversed_adjacency_CDGAndReaching, 5
                )
                callee_results.update(reachable_nodes)

    return Intra_results, callee_results


def forward_traverse(start_node, adjacency_list, reversed_adjacency_CDGAndReaching, base_path):

    Intra_reaching_nodes = find_all_reachable_nodes_with_depth(start_node, reversed_adjacency_CDGAndReaching, 10)

    caller_results = set()

    if is_method_id(start_node, base_path):

        if start_node in adjacency_list["CALL"]:
            caller_state_nodes = adjacency_list["CALL"][start_node]
            for caller_state_node in caller_state_nodes:
                impacted_caller_state_nodes = find_all_reachable_nodes_with_depth(caller_state_node, reversed_adjacency_CDGAndReaching, 5)
                caller_results.update(impacted_caller_state_nodes)
    else:

        belonged_method_node = getContainMethodId(start_node, base_path)
        caller_results.add(belonged_method_node)

        if belonged_method_node in adjacency_list["CALL"]:
            caller_state_nodes = adjacency_list["CALL"][belonged_method_node]

            for caller_state_node in caller_state_nodes:
                caller = getContainMethodId(caller_state_node, base_path)
                caller_results.add(caller)
                impacted_caller_state_nodes = find_all_reachable_nodes_with_depth(caller_state_node, reversed_adjacency_CDGAndReaching, 5)
                caller_results.update(impacted_caller_state_nodes)

    return Intra_reaching_nodes, caller_results


def get_slice_node_info(adjacency_list, reversed_adjacency_CDGAndReaching, reversed_adjacency_CALL, line_ids, nodes, Csv_basePath,backward=False, forward=False):

    unique_combinations = set()
    for start_node in line_ids:
        if start_node not in nodes:
            print(f"Node {start_node} does not exist in the graph.")
            continue
        Intra_results = set()
        Inter_results = set()
        if backward:
            Intra_results, Inter_results = backward_traverse(start_node, adjacency_list, reversed_adjacency_CDGAndReaching, reversed_adjacency_CALL)
        if forward:
            Intra_results, Inter_results = forward_traverse(start_node, adjacency_list, reversed_adjacency_CDGAndReaching, Csv_basePath)

        Intra_line_numbers = get_line_numbers_for_nodes(Intra_results, Csv_basePath)
        Intra_node_file = get_filepath_for_node(Intra_results, Csv_basePath)

        Inter_line_numbers = get_line_numbers_for_nodes(Inter_results, Csv_basePath)
        Inter_node_file = get_filepath_for_node(Inter_results, Csv_basePath)

        empty_content_list = ['<empty>', 'N/A', 'NaN']
        for node_id in Intra_line_numbers:
            if node_id in Intra_node_file:
                line_number = Intra_line_numbers[node_id]
                file_path = Intra_node_file[node_id]
                if file_path is None or line_number is None or file_path in empty_content_list or line_number in empty_content_list:
                    continue
                unique_combinations.add((file_path, int(line_number)))

        for node_id in Inter_line_numbers:
            if node_id in Inter_node_file:
                line_number = Inter_line_numbers[node_id]
                file_path = Inter_node_file[node_id]
                if file_path is None or line_number is None or file_path in empty_content_list or line_number in empty_content_list:
                    continue
                unique_combinations.add((file_path, int(line_number)))

    return unique_combinations


def sliceToString(sliceMap, sliceType):
    result_str = ""
    for file_path, code_snippet in sliceMap.items():
        result_str += f"{sliceType}Slice in File: {file_path}\n{sliceType} Slice:\n{code_snippet}\n\n"
    result_str = result_str.strip()
    return result_str


def slicing_entrance(Csv_basePath, source_code_basePath, nodes, adjacency_list, reversed_adjacency_CDGAndReaching, reversed_adjacency_CALL, criterion_file, criterion_line):
    line_ids = get_node_id_for_line(criterion_file, criterion_line, Csv_basePath, source_code_basePath)

    if line_ids is None:
        print("No criterion ID found.")
        return None, None

    backward_unique_combinations = get_slice_node_info(adjacency_list, reversed_adjacency_CDGAndReaching, reversed_adjacency_CALL, line_ids, nodes, Csv_basePath, backward=True)
    forward_unique_combinations = get_slice_node_info(adjacency_list, reversed_adjacency_CDGAndReaching, reversed_adjacency_CALL, line_ids, nodes, Csv_basePath, forward=True)
    backward_results = get_Pos_content(backward_unique_combinations, source_code_basePath)
    froward_results = get_Pos_content(forward_unique_combinations, source_code_basePath)

    return sliceToString(backward_results,'Backward'), sliceToString(froward_results,'Forward')




