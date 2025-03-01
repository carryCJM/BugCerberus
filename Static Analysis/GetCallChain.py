import os
import ast
from collections import defaultdict
from pathlib import Path

class CallGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.call_graph = defaultdict(list)
        self.reverse_call_graph = defaultdict(list)
        self.file_to_functions = defaultdict(list)
        self.defined_functions = set()
        self.current_function = None
        self.current_file = None

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.defined_functions.add(node.name)
        self.file_to_functions[self.current_file].append(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for body_item in node.body:
            if isinstance(body_item, ast.FunctionDef):
                self.visit_FunctionDef(body_item)

    def visit_Lambda(self, node):
        lambda_name = f"lambda_{id(node)}"
        self.defined_functions.add(lambda_name)
        self.current_function = lambda_name
        self.file_to_functions[self.current_file].append(lambda_name)
        self.generic_visit(node)

    def visit_Call(self, node):
        callee_name = None
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                callee_name = f"{node.func.value.id}.{node.func.attr}"
            elif isinstance(node.func.value, ast.Attribute):
                callee_name = f"{ast.unparse(node.func.value)}.{node.func.attr}"
        if callee_name and self.current_function and callee_name in self.defined_functions:
            self.call_graph[self.current_function].append(callee_name)
            self.reverse_call_graph[callee_name].append(self.current_function)
        self.generic_visit(node)

def build_call_graph(directory):
    call_graph_builder = CallGraphBuilder()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                call_graph_builder.current_file = Path(file_path).name
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=file_path)
                        call_graph_builder.visit(tree)
                    except Exception as e:
                        print(f"Failed to parse {file_path}: {e}")
    return call_graph_builder.call_graph, call_graph_builder.reverse_call_graph, call_graph_builder.file_to_functions, call_graph_builder.defined_functions

def get_full_call_chain(func_name, call_graph, reverse_call_graph, file_to_functions, defined_functions):
    call_chains = []
    def dfs_forward(function, path, visited):
        if function in visited:
            return
        visited.add(function)
        path.append(function)
        if len(path) > 1:
            caller, callee = path[-2], path[-1]
            call_chains.append(f"{caller} calls {callee}")
        if function in call_graph:
            for callee in call_graph[function]:
                dfs_forward(callee, path, visited)
        path.pop()
        visited.remove(function)

    def dfs_backward(function, path, visited):
        if function in visited:
            return
        visited.add(function)
        path.append(function)
        if len(path) > 1:
            callee, caller = path[-2], path[-1]
            call_chains.append(f"{caller} calls {callee}")
        if function in reverse_call_graph:
            for caller in reverse_call_graph[function]:
                dfs_backward(caller, path, visited)
        path.pop()
        visited.remove(function)

    dfs_forward(func_name, [], set())
    dfs_backward(func_name, [], set())
    for file, functions in file_to_functions.items():
        if func_name in functions:
            call_chains.append(f"{file} calls {func_name}")
    return call_chains

def main():
    project_directory = ''
    call_graph, reverse_call_graph, file_to_functions, defined_functions = build_call_graph(project_directory)
    function_name = "get_full_call_chain"
    if function_name not in defined_functions:
        print(f"Function '{function_name}' is not defined in the project.")
        return
    call_chains = get_full_call_chain(function_name, call_graph, reverse_call_graph, file_to_functions, defined_functions)
    print(f"\nFull call chains for function '{function_name}':")
    if not call_chains:
        print(f"No calls found for function '{function_name}'.")
    else:
        for chain in call_chains:
            print(chain)
