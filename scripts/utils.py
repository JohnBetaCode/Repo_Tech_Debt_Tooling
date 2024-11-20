# ----------------------------------------------------------------
import os
import requests
import json
from datetime import datetime
import argparse
from datetime import date, timedelta
import matplotlib.pyplot as plt
from tabulate import tabulate


# ----------------------------------------------------------------
def get_github_issues_and_prs_history(
    url: str, accept: str, token: str, save: bool = True
):
    """
    Retrieves issues and pull requests from GitHub API with pagination support.

    Args:
        url (str): GitHub API endpoint URL.
        accept (str): GitHub API accept header value.
        token (str): GitHub authentication token.
        save (bool, optional): Whether to save results to file. Defaults to True.

    Returns:
        list: List of issues and pull requests from GitHub.

    Raises:
        EnvironmentError: If required URL or accept header are missing.
    """

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
        print(f"Github data saved in {filename}")

    return issues


# Function to save issues to a JSON file
def save_file(data: list, path: str, filename="file.json"):
    """
    Saves data to a JSON file.

    Args:
        data (list): Data to save to file.
        path (str): Directory path where to save the file.
        filename (str, optional): Name of the file. Defaults to "file.json".
    """
    with open(os.path.join(path, filename), "w") as f:
        json.dump(data, f, indent=4)


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


def get_open_issues_up_to_date(issues, target_date):
    """
    Retrieves a list of issues that were open (not closed) up to and including a specific date.
    This includes both currently open issues and issues that were closed after the target date.

    Args:
        issues (list): List of issues from the GitHub API.
        target_date (str or date): The target date, either as "YYYY-MM-DD" string or date object.

    Returns:
        list: A list of issues that were open as of the target date.
    """
    # Convert target_date to date object if it's a string
    if isinstance(target_date, str):
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        target_date_obj = target_date

    open_issues = []

    for issue in issues:
        # Parse the created_at date
        created_at_date = datetime.strptime(
            issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).date()

        # Skip issues created after the target date
        if created_at_date > target_date_obj:
            continue

        # If issue is currently open, include it
        if issue["state"] == "open":
            open_issues.append(issue)
        # If issue is closed, check if it was closed after the target date
        elif issue["closed_at"]:
            closed_at_date = datetime.strptime(
                issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ"
            ).date()
            if closed_at_date > target_date_obj:
                open_issues.append(issue)

    return open_issues


def get_week_start_date(year: int, week: int) -> date:
    """
    Gets the first day (Monday) of a specified week in a year.

    Args:
        year (int): The year for which to calculate the date
        week (int): The week number (1-52)

    Returns:
        date: Date object representing the Monday of the specified week

    Example:
        >>> get_week_start_date(2024, 1)
        datetime.date(2024, 1, 1)  # First Monday of 2024
    """
    # Find the first day of the year
    first_day = date(year, 1, 1)
    # Find the first Monday of the year
    if first_day.weekday() > 3:
        first_monday = first_day + timedelta(days=(7 - first_day.weekday()))
    else:
        first_monday = first_day - timedelta(days=first_day.weekday())
    # Add the weeks
    return first_monday + timedelta(weeks=week - 1)


def get_week_end_date(year: int, week: int) -> date:
    """
    Gets the last day (Sunday) of a specified week in a year.

    Args:
        year (int): The year for which to calculate the date
        week (int): The week number (1-52)

    Returns:
        date: Date object representing the Sunday of the specified week

    Example:
        >>> get_week_end_date(2024, 1)
        datetime.date(2024, 1, 7)  # First Sunday of 2024
    """
    # Get Monday of the week
    monday = get_week_start_date(year, week)
    # Add 6 days to get to Sunday
    return monday + timedelta(days=6)


def get_issues_created_between_dates(issues, start_date, end_date):
    """
    Retrieves a list of issues that were created between two dates (inclusive).

    Args:
        issues (list): List of issues from the GitHub API.
        start_date (str or date): The start date, either as "YYYY-MM-DD" string or date object.
        end_date (str or date): The end date, either as "YYYY-MM-DD" string or date object.

    Returns:
        list: A list of issues created between start_date and end_date (inclusive).
    """
    # Convert dates to date objects if they're strings
    if isinstance(start_date, str):
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start_date_obj = start_date

    if isinstance(end_date, str):
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date_obj = end_date

    created_issues = []

    for issue in issues:
        # Parse the created_at date
        created_at_date = datetime.strptime(
            issue["created_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).date()

        # Check if the issue was created within the date range
        if start_date_obj <= created_at_date <= end_date_obj:
            created_issues.append(issue)

    return created_issues


def get_issues_closed_between_dates(issues, start_date, end_date):
    """
    Retrieves a list of issues that were closed between two dates (inclusive).

    Args:
        issues (list): List of issues from the GitHub API.
        start_date (str or date): The start date, either as "YYYY-MM-DD" string or date object.
        end_date (str or date): The end date, either as "YYYY-MM-DD" string or date object.

    Returns:
        list: A list of issues closed between start_date and end_date (inclusive).
    """
    # Convert dates to date objects if they're strings
    if isinstance(start_date, str):
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start_date_obj = start_date

    if isinstance(end_date, str):
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_date_obj = end_date

    closed_issues = []

    for issue in issues:
        # Skip if issue is not closed or has no closed_at date
        if issue["state"] != "closed" or not issue["closed_at"]:
            continue

        # Parse the closed_at date
        closed_at_date = datetime.strptime(
            issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ"
        ).date()

        # Check if the issue was closed within the date range
        if start_date_obj <= closed_at_date <= end_date_obj:
            closed_issues.append(issue)

    return closed_issues


def categorize_issues_by_priority(issues: list) -> dict:
    """
    Categorizes issues based on their priority labels and calculates scores.

    Priority scoring:
    - PRIORITY_LOW: 1 point
    - PRIORITY_MEDIUM: 2 points
    - PRIORITY_HIGH: 3 points
    - PRIORITY_SATANIC: 5 points
    - No priority label: Categorized as UNCATEGORIZED

    Args:
        issues (list): List of issues to categorize

    Returns:
        dict: Dictionary with categories as keys, containing score and count information
        Example:
        {
            'PRIORITY_LOW': {'total_score': 5, 'issue_count': 5},
            'PRIORITY_MEDIUM': {'total_score': 8, 'issue_count': 4},
            'UNCATEGORIZED': {'total_score': 0, 'issue_count': 3}
        }
    """
    # Initialize categories dictionary
    categories = {
        "PRIORITY_LOW": {"total_score": 0, "issue_count": 0},
        "PRIORITY_MEDIUM": {"total_score": 0, "issue_count": 0},
        "PRIORITY_HIGH": {"total_score": 0, "issue_count": 0},
        "PRIORITY_SATANIC": {"total_score": 0, "issue_count": 0},
        "UNCATEGORIZED": {"total_score": 0, "issue_count": 0},
    }

    # Priority scores mapping
    priority_scores = {
        "PRIORITY_LOW": 1,
        "PRIORITY_MEDIUM": 2,
        "PRIORITY_HIGH": 3,
        "PRIORITY_SATANIC": 5,
    }

    for issue in issues:
        priority_found = False

        # Check labels for priority
        for label in issue["labels"]:
            label_name = label["name"]
            if label_name in priority_scores:
                score = priority_scores[label_name]
                categories[label_name]["total_score"] += score
                categories[label_name]["issue_count"] += 1
                priority_found = True
                break

        # If no priority label found, count as uncategorized
        if not priority_found:
            categories["UNCATEGORIZED"]["issue_count"] += 1

    return categories


def create_issues_activity_graph(
    issues_data: list,
    start_week: int,
    end_week: int,
    current_year: int,
    save_path: str = "/workspace/tmp",
) -> None:
    """
    Creates and saves a graph showing weekly GitHub issues activity.
    Uses bars for created/closed issues and line for open issues.

    Args:
        issues_data (list): List of GitHub issues
        start_week (int): Starting week number (1-52)
        end_week (int): Ending week number (1-52)
        current_year (int): Year for the analysis
        save_path (str, optional): Directory to save the graph. Defaults to "/workspace/tmp"

    Returns:
        None: Saves the graph as 'issues_activity.png'
    """
    # Collect data for plotting
    weeks = list(range(start_week, end_week + 1))
    open_issues_data = []
    created_issues_data = []
    closed_issues_data = []

    for week in weeks:
        week_start = get_week_start_date(current_year, week)
        week_end = get_week_end_date(current_year, week)

        open_count = len(get_open_issues_up_to_date(issues_data, week_end))
        created_count = len(
            get_issues_created_between_dates(issues_data, week_start, week_end)
        )
        closed_count = len(
            get_issues_closed_between_dates(issues_data, week_start, week_end)
        )

        open_issues_data.append(open_count)
        created_issues_data.append(created_count)
        closed_issues_data.append(closed_count)

    # Create the visualization
    plt.figure(figsize=(12, 6))

    # Plot bars for created and closed issues
    bar_width = 0.35
    bar_positions_created = [x - bar_width / 2 for x in weeks]
    bar_positions_closed = [x + bar_width / 2 for x in weeks]

    plt.bar(
        bar_positions_created,
        created_issues_data,
        bar_width,
        label="# Created Issues",
        color="g",
        alpha=0.6,
    )
    plt.bar(
        bar_positions_closed,
        closed_issues_data,
        bar_width,
        label="# Closed Issues",
        color="r",
        alpha=0.6,
    )

    # Plot line for open issues
    plt.plot(
        weeks,
        open_issues_data,
        "b:",
        label="# Open Issues at the end of the week",
        marker="o",
        linewidth=2,
    )

    # Add value labels
    for i, value in enumerate(created_issues_data):
        plt.text(bar_positions_created[i], value, str(value), ha="center", va="bottom")
    for i, value in enumerate(closed_issues_data):
        plt.text(bar_positions_closed[i], value, str(value), ha="center", va="bottom")
    for i, value in enumerate(open_issues_data):
        plt.text(weeks[i], value, str(value), ha="center", va="bottom")

    plt.title("GitHub Issues Activity by Week")
    plt.xlabel("Week Number")
    plt.ylabel("Number of Issues")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()

    # Force x-axis to show all weeks
    plt.xticks(weeks)  # Add this line to show all week numbers
    plt.xlim(min(weeks) - 0.5, max(weeks) + 0.5)  # Add some padding on sides

    # Save the plot
    plt.savefig(
        os.path.join(save_path, "issues_activity.png"), bbox_inches="tight", dpi=300
    )
    print("Graph saved as 'issues_activity.png'")
    plt.close()


def create_issues_score_graph(
    issues_data: list,
    start_week: int,
    end_week: int,
    current_year: int,
    save_path: str = "/workspace/tmp",
) -> None:
    """
    Creates and saves a graph showing weekly GitHub issues scores based on priority.
    Uses bars for created/closed issues scores and line for open issues scores.

    Args:
        issues_data (list): List of GitHub issues
        start_week (int): Starting week number (1-52)
        end_week (int): Ending week number (1-52)
        current_year (int): Year for the analysis
        save_path (str, optional): Directory to save the graph. Defaults to "/workspace/tmp"

    Returns:
        None: Saves the graph as 'issues_score.png'
    """
    weeks = list(range(start_week, end_week + 1))
    open_scores = []
    created_scores = []
    closed_scores = []

    for week in weeks:
        week_start = get_week_start_date(current_year, week)
        week_end = get_week_end_date(current_year, week)

        # Get issues for each category
        open_issues = get_open_issues_up_to_date(issues_data, week_end)
        created_issues = get_issues_created_between_dates(
            issues_data, week_start, week_end
        )
        closed_issues = get_issues_closed_between_dates(
            issues_data, week_start, week_end
        )

        # Calculate scores for each category
        open_categories = categorize_issues_by_priority(open_issues)
        created_categories = categorize_issues_by_priority(created_issues)
        closed_categories = categorize_issues_by_priority(closed_issues)

        # Sum up total scores
        open_score = sum(cat["total_score"] for cat in open_categories.values())
        created_score = sum(cat["total_score"] for cat in created_categories.values())
        closed_score = sum(cat["total_score"] for cat in closed_categories.values())

        open_scores.append(open_score)
        created_scores.append(created_score)
        closed_scores.append(closed_score)

    # Create the visualization
    plt.figure(figsize=(12, 6))

    # Plot bars for created and closed issues scores
    bar_width = 0.35
    bar_positions_created = [x - bar_width / 2 for x in weeks]
    bar_positions_closed = [x + bar_width / 2 for x in weeks]

    plt.bar(
        bar_positions_created,
        created_scores,
        bar_width,
        label="Created Issues Score",
        color="g",
        alpha=0.6,
    )
    plt.bar(
        bar_positions_closed,
        closed_scores,
        bar_width,
        label="Closed Issues Score",
        color="r",
        alpha=0.6,
    )

    # Plot line for open issues scores
    plt.plot(
        weeks,
        open_scores,
        "b:",
        label="Open Issues Score at week end",
        marker="o",
        linewidth=2,
    )

    # Add value labels
    for i, value in enumerate(created_scores):
        plt.text(bar_positions_created[i], value, str(value), ha="center", va="bottom")
    for i, value in enumerate(closed_scores):
        plt.text(bar_positions_closed[i], value, str(value), ha="center", va="bottom")
    for i, value in enumerate(open_scores):
        plt.text(weeks[i], value, str(value), ha="center", va="bottom")

    plt.title("GitHub Issues Priority Scores by Week")
    plt.xlabel("Week Number")
    plt.ylabel("Priority Score")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()

    # Force x-axis to show all weeks
    plt.xticks(weeks)
    plt.xlim(min(weeks) - 0.5, max(weeks) + 0.5)

    # Save the plot
    plt.savefig(
        os.path.join(save_path, "issues_score.png"), bbox_inches="tight", dpi=300
    )
    print("Graph saved as 'issues_score.png'")
    plt.close()


def get_unique_users_from_issues(issues: list) -> list:
    """
    Extracts a list of unique usernames from issues' assignees.

    Args:
        issues (list): List of GitHub issues

    Returns:
        list: Sorted list of unique usernames who have been assigned to issues

    Example:
        >>> issues_data = load_issues_from_file(path="/workspace/tmp", filename="issues.json")
        >>> unique_users = get_unique_users_from_issues(issues_data)
        >>> print(unique_users)
        ['user1', 'user2', 'user3']
    """
    unique_users = set()

    for issue in issues:
        # Add assignees only
        if issue.get("assignees"):
            for assignee in issue["assignees"]:
                if assignee.get("login"):
                    unique_users.add(assignee["login"])

    return sorted(list(unique_users))


def create_user_issues_activity_graph(
    issues_data: list,
    start_week: int,
    end_week: int,
    current_year: int,
    username: str,
    save_path: str = "/workspace/tmp",
) -> None:
    """
    Creates and saves a graph showing weekly GitHub issues activity for a specific user.
    Uses bars for created/closed issues and line for open issues.

    Args:
        issues_data (list): List of GitHub issues
        start_week (int): Starting week number (1-52)
        end_week (int): Ending week number (1-52)
        current_year (int): Year for the analysis
        username (str): GitHub username to filter issues
        save_path (str, optional): Directory to save the graph. Defaults to "/workspace/tmp"
    """
    # Filter issues for the specific user
    user_issues = [
        issue
        for issue in issues_data
        if any(
            assignee.get("login") == username for assignee in issue.get("assignees", [])
        )
    ]

    # Initialize data structures for tracking weekly counts
    weeks_range = range(start_week, end_week + 1)
    created_issues = {week: 0 for week in weeks_range}
    closed_issues = {week: 0 for week in weeks_range}
    open_issues = {week: 0 for week in weeks_range}

    # Process each issue
    for issue in user_issues:
        created_date = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        closed_date = (
            None
            if not issue["closed_at"]
            else datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
        )

        if created_date.year == current_year:
            created_week = created_date.isocalendar()[1]
            if start_week <= created_week <= end_week:
                created_issues[created_week] += 1

        if closed_date and closed_date.year == current_year:
            closed_week = closed_date.isocalendar()[1]
            if start_week <= closed_week <= end_week:
                closed_issues[closed_week] += 1

    # Calculate running total of open issues
    running_total = 0
    for week in weeks_range:
        running_total += created_issues[week] - closed_issues[week]
        open_issues[week] = running_total

    # Create the visualization
    plt.figure(figsize=(15, 7))
    weeks = list(weeks_range)

    plt.bar(
        weeks, [created_issues[w] for w in weeks], label="Created Issues", alpha=0.6
    )
    plt.bar(weeks, [closed_issues[w] for w in weeks], label="Closed Issues", alpha=0.6)
    plt.plot(
        weeks,
        [open_issues[w] for w in weeks],
        label="Open Issues",
        color="red",
        linewidth=2,
    )

    plt.xlabel("Week Number")
    plt.ylabel("Number of Issues")
    plt.title(f"GitHub Issues Activity by Week for {username}")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Change filename to start with username
    filename = f"{username}_activity.png"
    plt.savefig(os.path.join(save_path, filename), bbox_inches="tight", dpi=300)
    print(f"Graph saved as '{filename}'")
    plt.close()


def create_user_issues_score_graph(
    issues_data: list,
    start_week: int,
    end_week: int,
    current_year: int,
    username: str,
    save_path: str = "/workspace/tmp",
) -> None:
    """
    Creates and saves a graph showing weekly GitHub issues scores for a specific user.
    Uses bars for created/closed issues scores and line for open issues scores.

    Args:
        issues_data (list): List of GitHub issues
        start_week (int): Starting week number (1-52)
        end_week (int): Ending week number (1-52)
        current_year (int): Year for the analysis
        username (str): GitHub username to filter issues
        save_path (str, optional): Directory to save the graph. Defaults to "/workspace/tmp"
    """
    # Filter issues for the specific user
    user_issues = [
        issue
        for issue in issues_data
        if any(
            assignee.get("login") == username for assignee in issue.get("assignees", [])
        )
    ]

    # Initialize data structures for tracking weekly scores
    weeks_range = range(start_week, end_week + 1)
    created_scores = {week: 0 for week in weeks_range}
    closed_scores = {week: 0 for week in weeks_range}
    open_scores = {week: 0 for week in weeks_range}

    # Process each issue
    for issue in user_issues:
        score = calculate_issue_score(issue)
        created_date = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        closed_date = (
            None
            if not issue["closed_at"]
            else datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
        )

        if created_date.year == current_year:
            created_week = created_date.isocalendar()[1]
            if start_week <= created_week <= end_week:
                created_scores[created_week] += score

        if closed_date and closed_date.year == current_year:
            closed_week = closed_date.isocalendar()[1]
            if start_week <= closed_week <= end_week:
                closed_scores[closed_week] += score

    # Calculate running total of open issue scores
    running_total = 0
    for week in weeks_range:
        running_total += created_scores[week] - closed_scores[week]
        open_scores[week] = running_total

    # Create the visualization
    plt.figure(figsize=(15, 7))
    weeks = list(weeks_range)

    plt.bar(
        weeks,
        [created_scores[w] for w in weeks],
        label="Created Issues Score",
        alpha=0.6,
    )
    plt.bar(
        weeks, [closed_scores[w] for w in weeks], label="Closed Issues Score", alpha=0.6
    )
    plt.plot(
        weeks,
        [open_scores[w] for w in weeks],
        label="Open Issues Score",
        color="red",
        linewidth=2,
    )

    plt.xlabel("Week Number")
    plt.ylabel("Issue Score")
    plt.title(f"GitHub Issues Priority Scores by Week for {username}")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Change filename to start with username
    filename = f"{username}_score.png"
    plt.savefig(os.path.join(save_path, filename), bbox_inches="tight", dpi=300)
    print(f"\nGraph saved as '{filename}'")
    plt.close()


def get_unique_users_from_issues(issues_data: list) -> list:
    """
    Extract unique users from issues assignees.

    Args:
        issues_data (list): List of GitHub issues

    Returns:
        list: List of unique usernames
    """
    unique_users = set()
    for issue in issues_data:
        for assignee in issue.get("assignees", []):
            unique_users.add(assignee.get("login"))
    return sorted(list(unique_users))


def calculate_issue_score(issue: dict) -> int:
    """
    Calculates the priority score for a single issue based on its priority labels.

    Priority scoring:
    - PRIORITY_LOW: 1 point
    - PRIORITY_MEDIUM: 2 points
    - PRIORITY_HIGH: 3 points
    - PRIORITY_SATANIC: 5 points
    - No priority label: 0 points

    Args:
        issue (dict): A single GitHub issue dictionary

    Returns:
        int: Priority score for the issue
    """
    # Priority scores mapping
    priority_scores = {
        "PRIORITY_LOW": 1,
        "PRIORITY_MEDIUM": 2,
        "PRIORITY_HIGH": 3,
        "PRIORITY_SATANIC": 5,
    }

    # Check labels for priority
    for label in issue.get("labels", []):
        label_name = label.get("name", "")
        if label_name in priority_scores:
            return priority_scores[label_name]

    # Return 0 if no priority label found
    return 0


def create_pdf_report(
    start_week: int, end_week: int, save_path: str = "/workspace/tmp"
) -> None:
    """
    Creates a single-page PDF report with all PNG files arranged vertically with margins.
    Uses letter width (8.5 inches) and adjusts height based on content.

    Args:
        start_week (int): Starting week number
        end_week (int): Ending week number
        save_path (str, optional): Directory containing PNGs and where to save PDF. Defaults to "/workspace/tmp"
    """
    try:
        from PIL import Image
        from datetime import datetime

        # Get dates for filename
        start_date = get_week_start_date(datetime.now().year, start_week)
        end_date = get_week_end_date(datetime.now().year, end_week)

        # Create filename
        pdf_filename = (
            f"tech_debt_report_W{start_week}-{start_date}_to_W{end_week}-{end_date}.pdf"
        )
        pdf_path = os.path.join(save_path, pdf_filename)

        # Get all PNG files in directory
        png_files = [f for f in os.listdir(save_path) if f.endswith(".png")]
        if not png_files:
            print("No PNG files found to merge")
            return

        # Letter width and margins in pixels at 300 DPI
        DPI = 300
        LETTER_WIDTH = int(8.5 * DPI)  # 8.5 inches * 300 DPI
        MARGIN = int(0.5 * DPI)  # 0.5 inch margin
        SPACING = int(0.25 * DPI)  # 0.25 inch spacing between images
        CONTENT_WIDTH = LETTER_WIDTH - (2 * MARGIN)

        # Process images and calculate total height needed
        processed_images = []
        total_height = MARGIN  # Start with top margin

        for png_file in png_files:
            # Open and process the PNG
            image_path = os.path.join(save_path, png_file)
            img = Image.open(image_path)
            if img.mode == "RGBA":
                img = img.convert("RGB")

            # Scale image to fit content width while maintaining aspect ratio
            scale = CONTENT_WIDTH / img.width
            new_width = CONTENT_WIDTH
            new_height = int(img.height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            processed_images.append(img)
            total_height += new_height + SPACING

        total_height += MARGIN - SPACING  # Add bottom margin and remove last spacing

        # Create the final image
        final_image = Image.new("RGB", (LETTER_WIDTH, total_height), "white")
        y_position = MARGIN

        # Paste all images
        for img in processed_images:
            x_position = MARGIN
            final_image.paste(img, (x_position, y_position))
            y_position += img.height + SPACING

        # Save as PDF
        final_image.save(pdf_path, resolution=DPI)
        print(f"PDF report saved as '{pdf_filename}'")

    except ImportError:
        print(
            "Error: PIL (Pillow) library is required. Install it using: pip install Pillow"
        )
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")


# ----------------------------------------------------------------
if __name__ == "__main__":

    # --------------------------------------------------------------
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Process GitHub issues based on week numbers"
    )
    parser.add_argument("--start-week", type=int, help="Starting week number (1-52)")
    parser.add_argument("--end-week", type=int, help="Ending week number (1-52)")
    args = parser.parse_args()

    # Get current year and week
    today = date.today()
    current_year = today.year
    current_week = today.isocalendar()[1]

    # Set default values if arguments are not provided
    start_week = args.start_week if args.start_week is not None else 1
    end_week = args.end_week if args.end_week is not None else current_week

    # Validate week numbers
    if not (1 <= start_week <= 52 and 1 <= end_week <= 52):
        print("Week numbers must be between 1 and 52")
        exit(1)
    if start_week > end_week:
        print("Start week must be less than or equal to end week")
        exit(1)

    start_date = get_week_start_date(current_year, start_week)
    end_date = get_week_end_date(current_year, end_week)

    print(
        f"Analyzing issues from Week {start_week} ({start_date}) to Week {end_week} ({end_date})"
    )

    # --------------------------------------------------------------
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
        print("Downloading data from Github API ...")
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
    # Iterate over the weeks for issues analysis
    # Initialize table data
    table_data = []
    headers = ["Week", "Open Issues", "Created Issues", "Closed Issues", "Score"]
    
    for week in range(start_week, end_week + 1):
        # ----------------------------------------------------------
        # Get issues opened up to date
        open_issues_up_to_date = get_open_issues_up_to_date(
            issues=issues_data, target_date=get_week_end_date(current_year, week)
        )

        # Get issues created and closed during this week
        week_start = get_week_start_date(current_year, week)
        week_end = get_week_end_date(current_year, week)
        issues_created_this_week = get_issues_created_between_dates(
            issues=issues_data, start_date=week_start, end_date=week_end
        )
        issues_closed_this_week = get_issues_closed_between_dates(
            issues=issues_data, start_date=week_start, end_date=week_end
        )

        categories = categorize_issues_by_priority(issues_closed_this_week)
        total_score = sum(cat["total_score"] for cat in categories.values())
        
        # Add row to table data
        table_data.append([
            week,
            len(open_issues_up_to_date),
            len(issues_created_this_week),
            len(issues_closed_this_week),
            total_score
        ])

    # Print table only if PRINT_LOGS_ANALYSIS_RESULTS is true
    if os.getenv("PRINT_LOGS_ANALYSIS_RESULTS", "false").lower() == "true":
        print("\nWeekly Issues Summary:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Create activity graph only if PERFORM_SCORE_ANALYSIS is true
    if os.getenv("PERFORM_QUANTITATIVE_ANALYSIS", "false").lower() == "true":
        create_issues_activity_graph(
            issues_data=issues_data,
            start_week=start_week,
            end_week=end_week,
            current_year=current_year,
        )

    # Create score graph only if PERFORM_SCORE_ANALYSIS is true
    if os.getenv("PERFORM_SCORE_ANALYSIS", "false").lower() == "true":
        create_issues_score_graph(
            issues_data=issues_data,
            start_week=start_week,
            end_week=end_week,
            current_year=current_year,
        )

    # --------------------------------------------------------------
    # Perform user analysis only if PERFORM_USER_ANALYSIS is true
    if os.getenv("PERFORM_USER_ANALYSIS", "true").lower() == "true":
        # Iterate over the weeks for user analysis
        unique_users = get_unique_users_from_issues(issues_data)
        print("\nUnique active users involved in issues:")
        for user in unique_users:
            print(f"- {user}")

        print("\nCreating graphs for each user:")
        for user in unique_users:
            create_user_issues_activity_graph(
                issues_data=issues_data,
                start_week=start_week,
                end_week=end_week,
                current_year=current_year,
                username=user,
            )
            create_user_issues_score_graph(
                issues_data=issues_data,
                start_week=start_week,
                end_week=end_week,
                current_year=current_year,
                username=user,
            )

    # --------------------------------------------------------------
    # After creating all graphs, merge them into PDF
    create_pdf_report(start_week, end_week)

    exit()
