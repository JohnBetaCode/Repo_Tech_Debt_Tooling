# ----------------------------------------------------------------
import os
import requests
import json


# ----------------------------------------------------------------
def get_github_issues_history(url: str, accept: str, token: str, save: bool = True):

    # Check if required environment variables are set
    if not url or not accept:
        raise EnvironmentError(
            "Missing required environment variables: GITHUB_API_URL or GITHUB_TOKEN"
        )

    issues = []
    page = 1

    # Set up headers
    headers = {
        "Accept": accept,
        "Authorization": f"Bearer github_pat_{token}",
    }

    while page < 100:

        print(f"requesting issues for page {page}")

        response = requests.get(
            f"{url}?state=all&per_page=100&page={page}", headers=headers
        )
        if response.status_code != 200:
            print(f"Failed to retrieve data: {response.status_code} - {response.text}")
            break

        data = response.json()
        if not data:  # Stop if there's no more data
            break

        issues.extend(data)
        page += 1

    if save:
        filename = "issues.json"
        save_file(data=issues, path="/workspace/tmp", filename=filename)
        print(f"Issues saved to {filename}")

    return issues


# Function to save issues to a JSON file
def save_file(data: list, path: str, filename="file.json"):
    with open(os.path.join(path, filename), "w") as f:
        json.dump(data, f, indent=4)


def print_dict_with_indent(data):
    """
    Prints a dictionary with indentation for better readability.

    Parameters:
        data (dict): The dictionary to print.
    """
    print(json.dumps(data, indent=4))


def count_labels(data: list):

    labels_list = {}

    for item in data:
        for label in item["labels"]:
            label_name = label["name"]
            if label_name in labels_list.keys():
                labels_list[label_name] += 1
            else:
                labels_list[label_name] = 1

    return labels_list


def load_issues_from_file(path: str, filename: str):
    """
    Loads issues from a JSON file if it exists.
    Returns an empty list if the file does not exist.

    Parameters:
        filename (str): The name of the file to load issues from.

    Returns:
        list: A list of issues loaded from the file or an empty list if file doesn't exist.
    """
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            issues = json.load(f)
        print(f"Issues loaded from {file_path}")
        return issues
    else:
        print(f"{file_path} does not exist. Returning an empty list.")
        return []


def print_selected_keys(data, keys):
    """
    Prints only the specified keys from the dictionary.

    Parameters:
        data (dict): The dictionary to filter.
        keys (list): A list of keys to print from the dictionary.
    """
    selected_data = {key: data[key] for key in keys if key in data}
    print_dict_with_indent(selected_data)


# ----------------------------------------------------------------
if __name__ == "__main__":

    # Load the URL and headers from environment variables
    GITHUB_API_URL_ISSUES = str(
        os.getenv("GITHUB_API_URL_ISSUES")
    )  # Set this as your desired GitHub API endpoint
    GITHUB_ACCEPT = str(os.getenv("GITHUB_ACCEPT"))  # Default to GitHub v3 if not set
    GITHUB_TOKEN = str(os.getenv("GITHUB_TOKEN"))  # Bearer token without the prefix

    # Check if the file exist, otherwise load it
    data = load_issues_from_file(path="/workspace/tmp", filename="issues.json")
    if not len(data):
        data = get_github_issues_history(
            url=GITHUB_API_URL_ISSUES,
            accept=GITHUB_ACCEPT,
            token=GITHUB_TOKEN,
        )

    # print_dict_with_indent(data[-1])
    print(len(data))

    labels = count_labels(data=data)

    print_selected_keys(
        data=labels,
        keys=["SATANIC", "PRIORITY_LOW", "PRIORITY_MEDIUM", "PRIORITY_HIGH"],
    )
