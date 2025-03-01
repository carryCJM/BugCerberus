
import requests
import pyarrow.parquet as pq


def loadOriginalData(flag):
    dataPath = None
    if flag == 'train':
        dataPath = 'originalTrainData/train-00000-of-00001.parquet'
    elif flag == 'test':
        dataPath = 'lite-test-00000-of-00001.parquet'
    elif flag == 'dev':
        dataPath = 'originalTrainData/dev-00000-of-00001.parquet'
    parquet_file = pq.ParquetFile(dataPath)
    data = parquet_file.read().to_pandas()
    repo_list = data.iloc[:, 0]
    base_commit = data.iloc[:, 11]
    return repo_list.tolist(), base_commit.tolist()


def downloadProjects():
    repo_list, commit_list = loadOriginalData('test')
    # print(repo_list)

    failedDownloadCommits = []
    failedDownloadRepos = []

    data_length = len(repo_list)

    for index in range(data_length):
        repo = repo_list[index]
        commit = commit_list[index]
        url = "https://github.com/" + str(repo) + "/archive/" + str(commit) + ".zip"

        try:
            response = requests.get(url)

            with open("/" + str(commit) + ".zip", "wb") as file:
                file.write(response.content)

            print(str(commit) + "download complete."+ "("+str(index)+ " / " + str(data_length)+")")

        except Exception:

            print(str(commit) + "download failed." + "("+str(index)+ " / " + str(data_length)+")")
            failedDownloadCommits.append(commit)
            failedDownloadRepos.append(repo)

 


if __name__ == '__main__':
    downloadProjects()
