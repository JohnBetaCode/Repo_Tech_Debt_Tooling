# ----------------------------------------------------------------
import os
import requests
import json
from datetime import datetime


# ----------------------------------------------------------------
def get_github_issues_and_prs_history(
    url: str, accept: str, token: str, save: bool = True
):

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


def get_opened_issues_by_date(issues, target_date):
    """
    Filters opened issues by a specified target date.

    Args:
        issues (list): List of issues from the GitHub API.
        target_date (str): The target date in "YYYY-MM-DD" format.

    Returns:
        list: A list of open issues created on the specified date.
    """
    filtered_issues = []
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()

    for issue in issues:
        # Parse the created_at date
        created_at_date = datetime.strptime(
            issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).date()

        # Check if the issue is open and was created on the target date
        if issue["state"] == "open" and created_at_date == target_date_obj:
            filtered_issues.append(issue)

    return filtered_issues


def get_closed_issues_by_date(issues, target_date):
    """
    Retrieves a list of issues that were closed (or merged, if a pull request) on a specific date.

    Args:
        issues (list): List of issues from the GitHub API.
        target_date (str): The target date in "YYYY-MM-DD" format.

    Returns:
        list: A list of issues closed or merged on the specified date.
    """
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    closed_issues = []

    for issue in issues:
        # Check if the issue is closed and has a closed_at date
        if issue["state"] == "closed" and "closed_at" in issue and issue["closed_at"]:
            closed_at_date = datetime.strptime(
                issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ"
            ).date()

            # Check if the issue was closed on the target date
            if closed_at_date == target_date_obj:
                closed_issues.append(issue)

    return closed_issues


def get_open_issues_up_to_date(issues, target_date):
    """
    Retrieves a list of open issues that were created up to (and including) a specific date,
    ignoring closed or merged issues.

    Args:
        issues (list): List of issues from the GitHub API.
        target_date (str): The target date in "YYYY-MM-DD" format.

    Returns:
        list: A list of open issues that were created up to the specified date.
    """
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    open_issues = []

    for issue in issues:
        # Check if the issue is open
        if issue["state"] == "open":
            # Parse the created_at date
            created_at_date = datetime.strptime(
                issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            ).date()

            # Check if the issue was created on or before the target date
            if created_at_date <= target_date_obj:
                open_issues.append(issue)

    return open_issues


def get_score_labels(labels: dict) -> dict:

    labels_score = {
        "PRIORITY_LOW": 1,
        "PRIORITY_MEDIUM": 2,
        "PRIORITY_HIGH": 3,
        "PRIORITY_SATANIC": 5,
    }
    for key, value in labels_score.items():
        if key in labels.keys():
            labels_score[key] *= labels[key]
        else:
            labels_score[key] = 0

    return labels_score


# ----------------------------------------------------------------
if __name__ == "__main__":

    # Check if the file exists and is not empty
    secrets_file = "configs/secrets.sh"
    if os.path.isfile(secrets_file) and os.path.getsize(secrets_file) > 0:
        # print("The secrets file exists and is not empty.")
        pass
    else:
        print("The secrets file is empty or does not exist.")
        exit()

    # --------------------------------------------------------------
    # Load the URL and headers from environment variables
    GITHUB_API_URL_ISSUES = str(
        os.getenv("GITHUB_API_URL_ISSUES")
    )  # Set this as your desired GitHub API endpoint
    GITHUB_ACCEPT = str(os.getenv("GITHUB_ACCEPT"))  # Default to GitHub v3 if not set
    GITHUB_TOKEN = str(os.getenv("GITHUB_TOKEN"))  # Bearer token without the prefix

    # --------------------------------------------------------------
    # Check if the file exist, otherwise load it
    data = load_issues_from_file(path="/workspace/tmp", filename="issues.json")
    if not len(data):
        data = get_github_issues_and_prs_history(
            url=GITHUB_API_URL_ISSUES,
            accept=GITHUB_ACCEPT,
            token=GITHUB_TOKEN,
        )

    # --------------------------------------------------------------
    # Filter only issues
    issues_data = [issue for issue in data if "pull_request" not in issue]
    # Filter only pull request
    prs_data = [issue for issue in data if not "pull_request" not in issue]

    # --------------------------------------------------------------
    target_date = "2024-11-03"

    # open_issues_on_date = get_opened_issues_by_date(
    #     issues=issues_data, target_date=target_date
    # )
    # opened_issues_labels = count_labels(data=open_issues_on_date)
    # print_selected_keys(
    #     data=opened_issues_labels,
    #     keys=["SATANIC", "PRIORITY_LOW", "PRIORITY_MEDIUM", "PRIORITY_HIGH"],
    # )

    closed_issues_on_date = get_closed_issues_by_date(
        issues=issues_data, target_date=target_date
    )
    closed_issues_labels = count_labels(data=closed_issues_on_date)
    # print_selected_keys(
    #     data=closed_issues_labels,
    #     keys=["SATANIC", "PRIORITY_LOW", "PRIORITY_MEDIUM", "PRIORITY_HIGH"],
    # )

    open_issues_up_to_date = get_open_issues_up_to_date(
        issues=issues_data, target_date=target_date
    )

    open_up_date_issues_labels = count_labels(data=open_issues_up_to_date)
    # print_selected_keys(
    #     data=open_up_date_issues_labels,
    #     keys=["SATANIC", "PRIORITY_LOW", "PRIORITY_MEDIUM", "PRIORITY_HIGH"],
    # )

    # --------------------------------------------------------------
    score_labels = get_score_labels(labels=open_up_date_issues_labels)
    score_total = sum(score_labels.values())

    # --------------------------------------------------------------
    # Report Zone
    print("Issues Opened: " + str(len(open_issues_up_to_date)))
    print("Total Score: " + str(score_total))
    print("Scores:")
    print_dict_with_indent(score_labels)
    print("Quantities:")
    print_selected_keys(
        data=open_up_date_issues_labels,
        keys=["SATANIC", "PRIORITY_LOW", "PRIORITY_MEDIUM", "PRIORITY_HIGH"],
    )
