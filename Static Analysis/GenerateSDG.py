
import os
import signal
from multiprocessing import Pool

import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

from neo4j import GraphDatabase
import concurrent.futures



def find_index_ignore_case(array, target):
    target_lower = target.lower()
    for index, item in enumerate(array):
        if item.lower() == target_lower:
            return index
    return -1

def generateNeo4jCSVs(commit):
    sourcePath = '' + commit
    outputPath = '/' + commit + '/'
    command1 = 'JoernPath '+'./joern-parse ' + sourcePath +'; ./joern-export --repr=all --format=neo4jcsv'

    command4 = 'find /JoernPath/out -name \'nodes_*_cypher.csv\' -exec sed -i \'\' \"s,file:/,file://' + outputPath + ',\" {} \;'
    command5 = 'find /JoernPath/out -name \'edges_*_cypher.csv\' -exec sed -i \'\' \"s,file:/,file://' + outputPath + ',\" {} \;'
    command6 = 'mkdir ' + outputPath + '; cp -R /JoernPath/out/* ' + outputPath
    command7 = 'rm -rf' + ' /JoernPath/out'

    if os.path.isdir(outputPath):
        print(outputPath + " exist here")
    else:
        print("command 1")
        print(command1)
        os.system(command1)
        print("command 4")
        print(command4)
        os.system(command4)
        print("command 5")
        print(command5)
        os.system(command5)
        print("command 6")
        print(command6)
        os.system(command6)
        print("command 7")
        print(command7)
        os.system(command7)

def run_command(command):
    print(f"Running command: {command}")
    os.system(command)



def generateNEO4J(commit):
    outputPath = f''

    # Define commands
    command1 = 'neo4j start'
    command2 = 'cd neo4jPath'
    command3 = 'find ' + outputPath + ' -name \'nodes_*_cypher.csv\' -exec ./cypher-shell -u username -p password --file {} \;'
    command4 = 'find ' + outputPath + ' -name \'edges_CALL_cypher.csv\' -exec ./cypher-shell -u username -p password --file {} \;'
    command5 = 'find ' + outputPath + ' -name \'edges_REACHING_DEF_cypher.csv\' -exec ./cypher-shell -u username -p password --file {} \;'
    command6 = 'find ' + outputPath + ' -name \'edges_CONTAINS_cypher.csv\' -exec ./cypher-shell -u username -p password --file {} \;'
    command7 = 'find ' + outputPath + ' -name \'edges_CDG_cypher.csv\' -exec ./cypher-shell -u username -p password --file {} \;'

    # Execute command1 and command2 sequentially
    print("command 1")
    run_command(command1)
    print("command 2")
    run_command(command2)
    print("command 3")
    run_command(command3)

    # Run command3 to command7 in parallel
    commands_to_run_in_parallel = [command4, command5, command6, command7]
    num_processes = min(32, os.cpu_count())

        # Run parallel commands
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:  # Adjust the number of processes based on your CPU
        futures = [executor.submit(run_command, cmd) for cmd in commands_to_run_in_parallel]

    print(f"{commit} project constructs successfully!")


def loadNeo4j():
    uri = "bolt://localhost:7687"
    username = ""
    password = ""
    driver = GraphDatabase.driver(uri, auth=(username, password))
    return driver


def clearNeo4j():
    driver = loadNeo4j()
    deleteCyper = """
                MATCH (n)
                DETACH DELETE n
                """
    with driver.session() as session:
        session.run(deleteCyper)
    print("neo4j dataset clear successfully")

