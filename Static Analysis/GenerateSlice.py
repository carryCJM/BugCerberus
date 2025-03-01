import pandas as pd
import os
import re
import traceback
import gc
import psutil

from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError

from tqdm import tqdm
from LoadCPGInfo import load_graph_data, reverse_adjacency_list
from CPGDependencyAnalysis import slicing_entrance


def clean_text(text):
    return re.sub(r'[\x00-\x09\x0B-\x1F\x7F-\x9F]', '', text)


def append_to_excel(data_rows, commit):
    ExcelPath = '/' + commit + '_statement_slice.xlsx'
    try:
        if not os.path.exists(ExcelPath):
            df_existing = pd.DataFrame(columns=[
                'commit', 'criterion_line', 'criterion_file', 'criterion_content',
                'backward_slice', 'forward_slice', 'fault_description'
            ])
            df_existing.to_excel(ExcelPath, index=False, engine='openpyxl')
        else:
            df_existing = pd.read_excel(ExcelPath, engine='openpyxl')

        cleaned_data_rows = [[clean_text(str(cell)) for cell in row] for row in data_rows]
        df_new = pd.DataFrame(cleaned_data_rows, columns=df_existing.columns)

        if not df_new.empty and not df_new.isna().all().all():
            df_updated = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_updated = df_existing

        df_updated.to_excel(ExcelPath, index=False, engine='openpyxl')
    except Exception as e:
        pass


def get_cri_content(file_path, cri_line):
    with open(file_path, 'r', encoding='utf-8', errors="ignore") as cf:
        lineContent = cf.readlines()[int(cri_line) - 1]
    return lineContent


def process_one_commit(commit, basePath, base_commits, diffs_list, problem_descriptions):
    try:
        if os.path.isdir('/' + str(commit)):
            return
        if os.path.isdir('/' + str(commit)):
            Csv_basePath = '/' + str(commit)
            os.makedirs('/' + str(commit))
        else:
            generateNeo4jCSVs(str(commit))
            Csv_basePath = '/' + str(commit)

        nodes, adjacency_list = load_graph_data(Csv_basePath)
        reversed_adjacency_CDGAndReaching = {
            edge_type: reverse_adjacency_list(adjacency_list[edge_type])
            for edge_type in ["CDG", "REACHING_DEF"]
        }
        reversed_adjacency_CALL = reverse_adjacency_list(adjacency_list["CALL"])
        source_code_basePath = basePath + '/' + str(commit)
        commit_index = find_index_ignore_case(base_commits, str(commit))
        diff_lines_return, modified_files_return = get_difflines_files(diffs_list[commit_index])
        problem_description = problem_descriptions[commit_index]

        one_commit_slice = []
        for index in range(len(modified_files_return)):
            diff_lines = diff_lines_return[index]
            criFile = modified_files_return[index]
            for diff_line in diff_lines:
                lineContent = get_cri_content(source_code_basePath + '/' + criFile, diff_line)
                if lineContent is None or lineContent.strip() == "":
                    continue
                backward_results, froward_results = slicing_entrance(
                    Csv_basePath, source_code_basePath, nodes,
                    adjacency_list, reversed_adjacency_CDGAndReaching,
                    reversed_adjacency_CALL, criFile, int(diff_line)
                )
                if backward_results is None or froward_results is None:
                    continue
                diff_slice = [
                    str(commit), str(diff_line), str(criFile), str(lineContent),
                    str(backward_results), str(froward_results), str(problem_description), str(1)
                ]
                one_commit_slice.append(diff_slice)

                if diff_line - 1 not in diff_lines:
                    backward_results, froward_results = None, None
                    lineContent = get_cri_content(source_code_basePath + '/' + criFile, diff_line - 1)
                    if lineContent is not None and lineContent.strip() != "":
                        backward_results, froward_results = slicing_entrance(
                            Csv_basePath, source_code_basePath, nodes, adjacency_list,
                            reversed_adjacency_CDGAndReaching, reversed_adjacency_CALL,
                            criFile, int(diff_line - 1)
                        )
                        if backward_results is not None and froward_results is not None:
                            diff_slice = [
                                str(commit), str(diff_line - 1), str(criFile), str(lineContent),
                                str(backward_results), str(froward_results), str(problem_description), str(0)
                            ]
                            one_commit_slice.append(diff_slice)

                if diff_line + 1 not in diff_lines:
                    backward_results, froward_results = None, None
                    lineContent = get_cri_content(source_code_basePath + '/' + criFile, diff_line + 1)
                    if lineContent is not None and lineContent.strip() != "":
                        backward_results, froward_results = slicing_entrance(
                            Csv_basePath, source_code_basePath, nodes, adjacency_list,
                            reversed_adjacency_CDGAndReaching, reversed_adjacency_CALL,
                            criFile, int(diff_line + 1)
                        )
                        if backward_results is not None and froward_results is not None:
                            diff_slice = [
                                str(commit), str(diff_line + 1), str(criFile), str(lineContent),
                                str(backward_results), str(froward_results), str(problem_description), str(0)
                            ]
                            one_commit_slice.append(diff_slice)

        if len(one_commit_slice) > 0:
            append_to_excel(one_commit_slice)
    except Exception as e:
        pass
    finally:
        if 'nodes' in locals():
            del nodes
        if 'adjacency_list' in locals():
            del adjacency_list
        gc.collect()


def generateEntrance(basePath):
    diffs_list, base_commits, problem_descriptions = loadOriginalData('train')
    folders = os.listdir(basePath)
    commits_to_process = [folder.title() for folder in folders if "." not in folder]
    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(
                process_one_commit, commit, basePath,
                base_commits, diffs_list, problem_descriptions
            ): commit
            for commit in commits_to_process
        }
        for future in tqdm(as_completed(futures), total=len(futures)):
            commit = futures[future]
            try:
                future.result(timeout=600)
            except TimeoutError:
                if hasattr(future, '_process') and future._process is not None:
                    proc_pid = future._process.pid
                    try:
                        parent = psutil.Process(proc_pid)
                        for child in parent.children(recursive=True):
                            child.kill()
                        parent.kill()
                    except Exception as e:
                        pass
            except Exception as e:
                traceback.print_exc()
