
import os

def read_specific_line(file_path, line_number):
    if not os.path.isfile(file_path):
        return None
    with open(file_path, 'r', encoding="utf-8", errors="ignore") as file:
        lines = file.readlines()
        if 0 < line_number <= len(lines):
            return lines[line_number - 1].strip()
    return None


def get_Pos_content(unique_combinations, source_basePath):

    unique_combinations_list = list(unique_combinations)
    unique_combinations_list.sort(key=lambda x: (x[0], x[1]))


    file_contents = {}

    for file_path, line_number in unique_combinations_list:
        code_line = read_specific_line(source_basePath + '/' + file_path, line_number)
        if code_line is not None:
            if file_path not in file_contents:
                file_contents[file_path] = code_line
            else:
                file_contents[file_path] += "\n" + code_line
    return file_contents

