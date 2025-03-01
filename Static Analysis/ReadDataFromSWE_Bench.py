import pyarrow.parquet as pq
import re


def loadOriginalData(flag):
    dataPath = None
    if flag == 'train':
        dataPath = '/train-00000-of-00001.parquet'
    elif flag == 'test':
        dataPath = '/test-00000-of-00001.parquet'
    elif flag == 'dev':
        dataPath = '/dev-00000-of-00001.parquet'
    parquet_file = pq.ParquetFile(dataPath)
    data = parquet_file.read().to_pandas()
    diffs_list = data.iloc[:, 3]
    base_commit = data.iloc[:, 2]
    return diffs_list.tolist(), base_commit.tolist()


def get_difflines_files(diff_content):
    diff_lines = []
    modified_files = []
    lines = diff_content.split('\n')
    currentFilePath = None
    current_range = None
    diff_line_count = 0
    for line in lines:

        onefile_diff_lines = []
        match = re.match(r'diff --git a/(.+) b/(.+)', line)
        if match and currentFilePath != match.group(2):

            currentFilePath = match.group(2)

        if line.startswith('@@'):
            diff_line_count = 0
            match = re.search(r'\-(\d+)(?:,(\d+))?', line)
            if match:
                start_line = int(match.group(1))
                line_count = int(match.group(2)) if match.group(2) else 1
                current_range = (start_line, start_line + line_count - 1)
        if line.startswith('-') and not line.startswith('---'):
            if current_range:
                start_line = current_range[0]
                deleted_line = start_line + diff_line_count - 1

                if deleted_line < current_range[1]:
                    onefile_diff_lines.append(deleted_line)

        if len(onefile_diff_lines) != 0 and currentFilePath is not None:
            diff_lines.append(onefile_diff_lines)
            modified_files.append(currentFilePath)
        diff_line_count += 1


    diff_lines_return = []
    modified_files_return = []
    for index in range(len(modified_files)):
        modified_file = modified_files[index]
        if modified_file in modified_files_return:
            file_index = modified_files_return.index(modified_file)
            diff_lines_return[file_index] = diff_lines_return[file_index].union(set(diff_lines[index]))
        else:
            modified_files_return.append(modified_file)
            file_lines_set = set(diff_lines[index])
            diff_lines_return.append(file_lines_set)

    return diff_lines_return, modified_files_return