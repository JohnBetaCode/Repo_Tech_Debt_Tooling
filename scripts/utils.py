# ----------------------------------------------------------------
import os
import requests
import json
from datetime import datetime
import argparse
from datetime import date, timedelta
import matplotlib.pyplot as plt
from tabulate import tabulate
import numpy as np


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
    Creates a single-page PDF report with PNG files arranged vertically in this order:
    1. Issues activity graph
    2. Issues score graph
    3. Issues severity graph
    4. User distribution pie charts

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

        # Define the order of PNG files
        ordered_png_files = [
            'issues_activity.png',
            'issues_score.png',
            'issues_priority_levels.png',
            f'user_distribution_week_{end_week}.png'
        ]

        # Filter existing PNG files while maintaining order
        png_files = [f for f in ordered_png_files if os.path.exists(os.path.join(save_path, f))]
        
        if not png_files:
            print("No PNG files found to merge")
            return

        # Rest of the function remains the same...
        DPI = 300
        LETTER_WIDTH = int(8.5 * DPI)
        MARGIN = int(0.5 * DPI)
        SPACING = int(0.25 * DPI)
        CONTENT_WIDTH = LETTER_WIDTH - (2 * MARGIN)

        # Process images and calculate total height needed
        processed_images = []
        total_height = MARGIN

        for png_file in png_files:
            image_path = os.path.join(save_path, png_file)
            img = Image.open(image_path)
            if img.mode == "RGBA":
                img = img.convert("RGB")

            scale = CONTENT_WIDTH / img.width
            new_width = CONTENT_WIDTH
            new_height = int(img.height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            processed_images.append(img)
            total_height += new_height + SPACING

        total_height += MARGIN - SPACING

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


def create_issues_score_levels_graph(
    issues_data: list,
    start_week: int,
    end_week: int,
    current_year: int,
    save_path: str = "/workspace/tmp",
) -> None:
    """
    Creates and saves a graph showing weekly GitHub issues by priority level.
    Shows stacked bars for each priority level with dual x-axes for weeks and months.

    Args:
        issues_data (list): List of GitHub issues
        start_week (int): Starting week number (1-52)
        end_week (int): Ending week number (1-52)
        current_year (int): Year for the analysis
        save_path (str, optional): Directory to save the graph. Defaults to "/workspace/tmp"
    """
    weeks = list(range(start_week, end_week + 1))
    priority_data = {
        "PRIORITY_LOW": [],
        "PRIORITY_MEDIUM": [],
        "PRIORITY_HIGH": [],
        "PRIORITY_SATANIC": [],
        "UNCATEGORIZED": []
    }

    # Collect data for each week
    for week in weeks:
        week_end = get_week_end_date(current_year, week)
        open_issues = get_open_issues_up_to_date(issues_data, week_end)
        categories = categorize_issues_by_priority(open_issues)
        
        for priority in priority_data.keys():
            priority_data[priority].append(categories[priority]["issue_count"])

    # Create the visualization with dual x-axes
    fig, ax1 = plt.subplots(figsize=(15, 8))
    
    # Create second x-axis for months
    ax2 = ax1.twiny()

    # Create stacked bar chart on primary axis
    bottom = np.zeros(len(weeks))
    colors = {
        "PRIORITY_LOW": "#7FBA00",      # Green
        "PRIORITY_MEDIUM": "#FFA500",    # Orange
        "PRIORITY_HIGH": "#F35325",      # Red
        "PRIORITY_SATANIC": "#8B0000",   # Dark Red
        "UNCATEGORIZED": "#A9A9A9"       # Gray
    }

    for priority, counts in priority_data.items():
        ax1.bar(weeks, counts, bottom=bottom, label=priority, color=colors[priority], alpha=0.7)
        bottom += np.array(counts)

        # Add value labels if count > 0
        for i, count in enumerate(counts):
            if count > 0:
                # Position the text in the middle of its segment
                height = bottom[i] - (count / 2)
                ax1.text(weeks[i], height, str(count), ha='center', va='center')

    # Set up the primary x-axis (weeks)
    ax1.set_xlim(min(weeks) - 0.5, max(weeks) + 0.5)
    ax1.set_xticks(weeks)
    ax1.set_xlabel("Week Number")
    
    # Set up the secondary x-axis (months)
    month_positions = []
    month_labels = []
    
    # Get unique months and their positions
    for week in weeks:
        week_start = get_week_start_date(current_year, week)
        month_name = week_start.strftime("%B")
        month_pos = week
        
        # Only add month if it's not already in labels or if it's the first week
        if not month_labels or month_labels[-1] != month_name:
            month_positions.append(month_pos)
            month_labels.append(month_name)
    
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(month_positions)
    ax2.set_xticklabels(month_labels)
    
    # Adjust layout to prevent label overlap
    plt.title("GitHub Issues by Priority Level per Week")
    ax1.set_ylabel("Number of Issues")
    ax1.grid(True, linestyle="--", alpha=0.7)
    
    # Move legend inside the plot area in the upper right corner
    ax1.legend(loc='upper left')

    # Remove the subplots_adjust call since we're keeping the legend inside
    # plt.subplots_adjust(right=0.85)  # Remove this line

    # Save the plot
    plt.savefig(
        os.path.join(save_path, "issues_priority_levels.png"), 
        bbox_inches="tight", 
        dpi=300
    )
    print("Graph saved as 'issues_priority_levels.png'")
    plt.close()


def create_users_pdf_report(
    start_week: int, end_week: int, save_path: str = "/workspace/tmp"
) -> None:
    """
    Creates a single PDF report with title page, index, and one page per user containing all their graphs.
    
    Args:
        start_week (int): Starting week number
        end_week (int): Ending week number
        save_path (str, optional): Base directory containing user folders. Defaults to "/workspace/tmp"
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        from datetime import datetime
        import glob

        # Get dates for filename
        start_date = get_week_start_date(datetime.now().year, start_week)
        end_date = get_week_end_date(datetime.now().year, end_week)

        # Constants for PDF layout
        DPI = 300
        LETTER_WIDTH = int(8.5 * DPI)
        LETTER_HEIGHT = int(11 * DPI)
        MARGIN = int(0.5 * DPI)
        SPACING = int(0.25 * DPI)
        CONTENT_WIDTH = LETTER_WIDTH - (2 * MARGIN)

        # Process user directories
        users_dir = os.path.join(save_path, "users")
        if not os.path.exists(users_dir):
            print("No users directory found")
            return

        # Collect all user PNGs
        users_data = []
        for user_dir in sorted(os.listdir(users_dir)):
            user_path = os.path.join(users_dir, user_dir)
            if os.path.isdir(user_path):
                user_pngs = sorted(glob.glob(os.path.join(user_path, "*.png")))
                if user_pngs:
                    users_data.append({
                        'username': user_dir,
                        'images': user_pngs
                    })

        if not users_data:
            print("No user PNG files found")
            return

        # Create pages list to store all pages
        pages = []

        # Create title page
        title_page = Image.new("RGB", (LETTER_WIDTH, LETTER_HEIGHT), "white")
        draw = ImageDraw.Draw(title_page)
        
        # Try to load a font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            regular_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            regular_font = ImageFont.load_default()

        # Add title page content
        title = "GitHub Issues Report"
        subtitle = f"Weeks {start_week} to {end_week}"
        date_range = f"({start_date} - {end_date})"
        
        # Calculate text positions for centering
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=regular_font)
        date_bbox = draw.textbbox((0, 0), date_range, font=regular_font)
        
        title_width = title_bbox[2] - title_bbox[0]
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        date_width = date_bbox[2] - date_bbox[0]
        
        draw.text(((LETTER_WIDTH - title_width) // 2, LETTER_HEIGHT // 3), title, font=title_font, fill="black")
        draw.text(((LETTER_WIDTH - subtitle_width) // 2, LETTER_HEIGHT // 2), subtitle, font=regular_font, fill="black")
        draw.text(((LETTER_WIDTH - date_width) // 2, LETTER_HEIGHT // 2 + 100), date_range, font=regular_font, fill="black")
        
        pages.append(title_page)

        # Create index page
        index_page = Image.new("RGB", (LETTER_WIDTH, LETTER_HEIGHT), "white")
        draw = ImageDraw.Draw(index_page)
        
        # Add index title
        index_title = "Index"
        index_bbox = draw.textbbox((0, 0), index_title, font=title_font)
        index_width = index_bbox[2] - index_bbox[0]
        draw.text(((LETTER_WIDTH - index_width) // 2, MARGIN), index_title, font=title_font, fill="black")
        
        # Add user list
        y_position = MARGIN + 150
        for i, user_data in enumerate(users_data, 1):
            entry = f"{i}. {user_data['username']}"
            draw.text((MARGIN, y_position), entry, font=regular_font, fill="black")
            y_position += 50

        pages.append(index_page)

        # Process each user's images
        for user_data in users_data:
            # Create new page for user
            user_page = Image.new("RGB", (LETTER_WIDTH, LETTER_HEIGHT), "white")
            draw = ImageDraw.Draw(user_page)
            
            # Add user title at the top
            user_title = f"User: {user_data['username']}"
            title_bbox = draw.textbbox((0, 0), user_title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((LETTER_WIDTH - title_width) // 2, MARGIN), user_title, font=title_font, fill="black")
            
            # Calculate layout for three graphs
            graph_height = (LETTER_HEIGHT - (4 * MARGIN)) // 3  # Divide remaining space by 3
            
            # Process and paste all three graphs
            for i, image_path in enumerate(user_data['images']):
                img = Image.open(image_path)
                if img.mode == "RGBA":
                    img = img.convert("RGB")

                # Scale image to fit width while maintaining aspect ratio
                scale = CONTENT_WIDTH / img.width
                new_width = CONTENT_WIDTH
                new_height = int(img.height * scale)
                
                # Further scale if height is too large
                if new_height > graph_height:
                    scale = graph_height / new_height
                    new_width = int(new_width * scale)
                    new_height = graph_height

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Calculate y position for each graph
                y_position = MARGIN + title_bbox[3] + SPACING  # Start after title
                if i == 1:  # Second graph
                    y_position += graph_height + SPACING
                elif i == 2:  # Third graph
                    y_position += (graph_height + SPACING) * 2

                # Center horizontally
                x_position = (LETTER_WIDTH - new_width) // 2
                
                # Paste image
                user_page.paste(img, (x_position, y_position))

            pages.append(user_page)

        # Create output filename and save PDF
        pdf_filename = f"user_reports_W{start_week}-{start_date}_to_W{end_week}-{end_date}.pdf"
        pdf_path = os.path.join(save_path, pdf_filename)
        
        # Save all pages to PDF
        pages[0].save(
            pdf_path,
            "PDF",
            resolution=DPI,
            save_all=True,
            append_images=pages[1:]
        )
        print(f"Users PDF report saved as '{pdf_filename}'")

    except ImportError:
        print("Error: PIL (Pillow) library is required. Install it using: pip install Pillow")
    except Exception as e:
        print(f"Error creating users PDF: {str(e)}")


def get_user_weekly_issues(
    issues_data: list,
    username: str,
    start_week: int,
    end_week: int,
    current_year: int
) -> list:
    """
    Gets the number of issues assigned to a user for each week.

    Args:
        issues_data (list): List of GitHub issues
        username (str): GitHub username to analyze
        start_week (int): Starting week number (1-52)
        end_week (int): Ending week number (1-52)
        current_year (int): Year for the analysis

    Returns:
        list: List of dictionaries containing week number and issue counts
        Example: [
            {'week': 1, 'open_issues': 5, 'created_issues': 2, 'closed_issues': 1},
            {'week': 2, 'open_issues': 6, 'created_issues': 3, 'closed_issues': 2},
            ...
        ]
    """
    weekly_data = []

    # Filter issues assigned to the user
    user_issues = [
        issue for issue in issues_data
        if any(assignee.get('login') == username for assignee in issue.get('assignees', []))
    ]

    for week in range(start_week, end_week + 1):
        week_start = get_week_start_date(current_year, week)
        week_end = get_week_end_date(current_year, week)

        # Get issues opened up to date
        open_issues = get_open_issues_up_to_date(user_issues, week_end)
        
        # Get issues created and closed during this week
        created_issues = get_issues_created_between_dates(
            user_issues, week_start, week_end
        )
        closed_issues = get_issues_closed_between_dates(
            user_issues, week_start, week_end
        )

        weekly_data.append({
            'week': week,
            'open_issues': len(open_issues),
            'created_issues': len(created_issues),
            'closed_issues': len(closed_issues)
        })

    return weekly_data


def create_user_issues_graph(
    user_weekly_data: list,
    username: str,
    save_path: str,
) -> None:
    """
    Creates and saves a graph showing weekly GitHub issues activity for a specific user.
    Uses bars for created/closed issues and line for open issues.

    Args:
        user_weekly_data (list): List of dictionaries containing weekly data for the user
        username (str): GitHub username
        save_path (str): Directory to save the graph
    """
    # Extract data for plotting
    weeks = [data['week'] for data in user_weekly_data]
    open_issues = [data['open_issues'] for data in user_weekly_data]
    created_issues = [data['created_issues'] for data in user_weekly_data]
    closed_issues = [data['closed_issues'] for data in user_weekly_data]

    # Create the visualization
    plt.figure(figsize=(12, 6))

    # Plot bars for created and closed issues
    bar_width = 0.35
    bar_positions_created = [x - bar_width/2 for x in weeks]
    bar_positions_closed = [x + bar_width/2 for x in weeks]

    plt.bar(
        bar_positions_created,
        created_issues,
        bar_width,
        label="Created Issues",
        color="g",
        alpha=0.6
    )
    plt.bar(
        bar_positions_closed,
        closed_issues,
        bar_width,
        label="Closed Issues",
        color="r",
        alpha=0.6
    )

    # Plot line for open issues
    plt.plot(
        weeks,
        open_issues,
        "b:",
        label="Open Issues at week end",
        marker="o",
        linewidth=2
    )

    # Add value labels
    for i, value in enumerate(created_issues):
        plt.text(bar_positions_created[i], value, str(value), ha='center', va='bottom')
    for i, value in enumerate(closed_issues):
        plt.text(bar_positions_closed[i], value, str(value), ha='center', va='bottom')
    for i, value in enumerate(open_issues):
        plt.text(weeks[i], value, str(value), ha='center', va='bottom')

    plt.title(f"GitHub Issues Activity for {username}")
    plt.xlabel("Week Number")
    plt.ylabel("Number of Issues")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()

    # Force x-axis to show all weeks
    plt.xticks(weeks)
    plt.xlim(min(weeks) - 0.5, max(weeks) + 0.5)

    # Save the plot
    plt.savefig(
        os.path.join(save_path, f"{username}_activity.png"),
        bbox_inches="tight",
        dpi=300
    )
    print(f"Graph saved for user {username}")
    plt.close()


def get_user_weekly_scores(
    issues_data: list,
    username: str,
    start_week: int,
    end_week: int,
    current_year: int
) -> list:
    """
    Gets the priority scores of issues assigned to a user for each week.

    Args:
        issues_data (list): List of GitHub issues
        username (str): GitHub username to analyze
        start_week (int): Starting week number (1-52)
        end_week (int): Ending week number (1-52)
        current_year (int): Year for the analysis

    Returns:
        list: List of dictionaries containing week number and issue scores
        Example: [
            {'week': 1, 'open_score': 5, 'created_score': 2, 'closed_score': 1},
            {'week': 2, 'open_score': 6, 'created_score': 3, 'closed_score': 2},
            ...
        ]
    """
    weekly_data = []

    # Filter issues assigned to the user
    user_issues = [
        issue for issue in issues_data
        if any(assignee.get('login') == username for assignee in issue.get('assignees', []))
    ]

    for week in range(start_week, end_week + 1):
        week_start = get_week_start_date(current_year, week)
        week_end = get_week_end_date(current_year, week)

        # Get issues for each category
        open_issues = get_open_issues_up_to_date(user_issues, week_end)
        created_issues = get_issues_created_between_dates(user_issues, week_start, week_end)
        closed_issues = get_issues_closed_between_dates(user_issues, week_start, week_end)

        # Calculate scores for each category
        open_categories = categorize_issues_by_priority(open_issues)
        created_categories = categorize_issues_by_priority(created_issues)
        closed_categories = categorize_issues_by_priority(closed_issues)

        # Sum up total scores
        open_score = sum(cat["total_score"] for cat in open_categories.values())
        created_score = sum(cat["total_score"] for cat in created_categories.values())
        closed_score = sum(cat["total_score"] for cat in closed_categories.values())

        weekly_data.append({
            'week': week,
            'open_score': open_score,
            'created_score': created_score,
            'closed_score': closed_score
        })

    return weekly_data


def create_user_scores_graph(
    user_weekly_data: list,
    username: str,
    save_path: str,
) -> None:
    """
    Creates and saves a graph showing weekly GitHub issues scores for a specific user.
    Uses bars for created/closed scores and line for open scores.

    Args:
        user_weekly_data (list): List of dictionaries containing weekly score data for the user
        username (str): GitHub username
        save_path (str): Directory to save the graph
    """
    # Extract data for plotting
    weeks = [data['week'] for data in user_weekly_data]
    open_scores = [data['open_score'] for data in user_weekly_data]
    created_scores = [data['created_score'] for data in user_weekly_data]
    closed_scores = [data['closed_score'] for data in user_weekly_data]

    # Create the visualization
    plt.figure(figsize=(12, 6))

    # Plot bars for created and closed scores
    bar_width = 0.35
    bar_positions_created = [x - bar_width/2 for x in weeks]
    bar_positions_closed = [x + bar_width/2 for x in weeks]

    plt.bar(
        bar_positions_created,
        created_scores,
        bar_width,
        label="Created Issues Score",
        color="g",
        alpha=0.6
    )
    plt.bar(
        bar_positions_closed,
        closed_scores,
        bar_width,
        label="Closed Issues Score",
        color="r",
        alpha=0.6
    )

    # Plot line for open scores
    plt.plot(
        weeks,
        open_scores,
        "b:",
        label="Open Issues Score at week end",
        marker="o",
        linewidth=2
    )

    # Add value labels
    for i, value in enumerate(created_scores):
        plt.text(bar_positions_created[i], value, str(value), ha='center', va='bottom')
    for i, value in enumerate(closed_scores):
        plt.text(bar_positions_closed[i], value, str(value), ha='center', va='bottom')
    for i, value in enumerate(open_scores):
        plt.text(weeks[i], value, str(value), ha='center', va='bottom')

    plt.title(f"GitHub Issues Priority Scores for {username}")
    plt.xlabel("Week Number")
    plt.ylabel("Priority Score")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()

    # Force x-axis to show all weeks
    plt.xticks(weeks)
    plt.xlim(min(weeks) - 0.5, max(weeks) + 0.5)

    # Save the plot
    plt.savefig(
        os.path.join(save_path, f"{username}_scores.png"),
        bbox_inches="tight",
        dpi=300
    )
    print(f"Score graph saved for user {username}")
    plt.close()


def create_user_distribution_charts(
    users_statistics: list,
    end_week: int,
    save_path: str = "/workspace/tmp"
) -> None:
    """
    Creates two side-by-side pie charts showing the distribution of issues and scores among users
    for the last analyzed week.

    Args:
        users_statistics (list): List of dictionaries containing user statistics
        end_week (int): The last week number being analyzed
        save_path (str): Directory to save the graph
    """
    # Skip if no data
    if not users_statistics:
        print("No user statistics available for creating distribution charts")
        return

    # Create figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    # Extract data for plotting
    usernames = [stat['username'] for stat in users_statistics]
    open_issues = [stat['open_issues'] for stat in users_statistics]
    total_scores = [stat['total_score'] for stat in users_statistics]

    # Calculate total values for percentage calculation
    total_issues = sum(open_issues)
    total_score = sum(total_scores)

    # Create labels with both count and percentage for issues
    issue_labels = [
        f'{user}\n({issues} issues)\n({issues/total_issues*100:.1f}%)'
        if issues > 0 else ''
        for user, issues in zip(usernames, open_issues)
    ]

    # Create labels with both score and percentage for scores
    score_labels = [
        f'{user}\n({score} points)\n({score/total_score*100:.1f}%)'
        if score > 0 else ''
        for user, score in zip(usernames, total_scores)
    ]

    # Remove empty labels and corresponding data
    issues_data = [(i, l) for i, l in zip(open_issues, issue_labels) if i > 0]
    scores_data = [(s, l) for s, l in zip(total_scores, score_labels) if s > 0]
    
    if issues_data:
        values_issues, labels_issues = zip(*issues_data)
    else:
        values_issues, labels_issues = [], []
    
    if scores_data:
        values_scores, labels_scores = zip(*scores_data)
    else:
        values_scores, labels_scores = [], []

    # Plot issues distribution
    if values_issues:
        wedges1, texts1, autotexts1 = ax1.pie(
            values_issues,
            labels=labels_issues,
            autopct='',  # We already include percentages in labels
            startangle=90
        )
    ax1.set_title(f'Issues Distribution - Week {end_week}\nTotal Issues: {total_issues}')

    # Plot scores distribution
    if values_scores:
        wedges2, texts2, autotexts2 = ax2.pie(
            values_scores,
            labels=labels_scores,
            autopct='',  # We already include percentages in labels
            startangle=90
        )
    ax2.set_title(f'Score Distribution - Week {end_week}\nTotal Score: {total_score}')

    # Add warning text at the bottom of the figure
    warning_text = (
        "Note: Issues and scores may be shared among multiple users.\n"
        "The total sum might exceed the individual issue counts due to shared assignments."
    )
    plt.figtext(
        0.5, 0.02,  # x, y position
        warning_text,
        ha='center',
        color='red',
        style='italic',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none')
    )

    # Adjust subplot parameters to make room for the warning text
    plt.subplots_adjust(bottom=0.15)

    # Save the plot
    plt.savefig(
        os.path.join(save_path, f'user_distribution_week_{end_week}.png'),
        bbox_inches='tight',
        dpi=300
    )
    print(f"User distribution charts saved for week {end_week}")
    plt.close()


def create_user_priority_levels_graph(
    issues_data: list,
    username: str,
    start_week: int,
    end_week: int,
    current_year: int,
    save_path: str,
) -> None:
    """
    Creates and saves a graph showing weekly GitHub issues by priority level for a specific user.
    Shows stacked bars for each priority level with dual x-axes for weeks and months.

    Args:
        issues_data (list): List of GitHub issues
        username (str): GitHub username
        start_week (int): Starting week number (1-52)
        end_week (int): Ending week number (1-52)
        current_year (int): Year for the analysis
        save_path (str): Directory to save the graph
    """
    weeks = list(range(start_week, end_week + 1))
    priority_data = {
        "PRIORITY_LOW": [],
        "PRIORITY_MEDIUM": [],
        "PRIORITY_HIGH": [],
        "PRIORITY_SATANIC": [],
        "UNCATEGORIZED": []
    }

    # Filter issues for this user
    user_issues = [
        issue for issue in issues_data
        if any(assignee.get('login') == username for assignee in issue.get('assignees', []))
    ]

    # Collect data for each week
    for week in weeks:
        week_end = get_week_end_date(current_year, week)
        open_issues = get_open_issues_up_to_date(user_issues, week_end)
        categories = categorize_issues_by_priority(open_issues)
        
        for priority in priority_data.keys():
            priority_data[priority].append(categories[priority]["issue_count"])

    # Create the visualization with dual x-axes
    fig, ax1 = plt.subplots(figsize=(15, 8))
    
    # Create second x-axis for months
    ax2 = ax1.twiny()

    # Create stacked bar chart on primary axis
    bottom = np.zeros(len(weeks))
    colors = {
        "PRIORITY_LOW": "#7FBA00",      # Green
        "PRIORITY_MEDIUM": "#FFA500",    # Orange
        "PRIORITY_HIGH": "#F35325",      # Red
        "PRIORITY_SATANIC": "#8B0000",   # Dark Red
        "UNCATEGORIZED": "#A9A9A9"       # Gray
    }

    for priority, counts in priority_data.items():
        ax1.bar(weeks, counts, bottom=bottom, label=priority, color=colors[priority], alpha=0.7)
        bottom += np.array(counts)

        # Add value labels if count > 0
        for i, count in enumerate(counts):
            if count > 0:
                # Position the text in the middle of its segment
                height = bottom[i] - (count / 2)
                ax1.text(weeks[i], height, str(count), ha='center', va='center')

    # Set up the primary x-axis (weeks)
    ax1.set_xlim(min(weeks) - 0.5, max(weeks) + 0.5)
    ax1.set_xticks(weeks)
    ax1.set_xlabel("Week Number")
    
    # Set up the secondary x-axis (months)
    month_positions = []
    month_labels = []
    
    # Get unique months and their positions
    for week in weeks:
        week_start = get_week_start_date(current_year, week)
        month_name = week_start.strftime("%B")
        month_pos = week
        
        # Only add month if it's not already in labels or if it's the first week
        if not month_labels or month_labels[-1] != month_name:
            month_positions.append(month_pos)
            month_labels.append(month_name)
    
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_xticks(month_positions)
    ax2.set_xticklabels(month_labels)
    
    plt.title(f"GitHub Issues by Priority Level for {username}")
    ax1.set_ylabel("Number of Issues")
    ax1.grid(True, linestyle="--", alpha=0.7)
    ax1.legend(loc='upper left')

    # Save the plot
    plt.savefig(
        os.path.join(save_path, f"{username}_priority_levels.png"),
        bbox_inches="tight",
        dpi=300
    )
    print(f"Priority levels graph saved for user {username}")
    plt.close()


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

    # --------------------------------------------------------------
    # Create activity graph only if PERFORM_SCORE_ANALYSIS is true
    if os.getenv("PERFORM_QUANTITATIVE_ANALYSIS", "false").lower() == "true":
        create_issues_activity_graph(
            issues_data=issues_data,
            start_week=start_week,
            end_week=end_week,
            current_year=current_year,
        )

    # --------------------------------------------------------------
    # Create score graph only if PERFORM_SCORE_ANALYSIS is true
    if os.getenv("PERFORM_SCORE_ANALYSIS", "false").lower() == "true":
        create_issues_score_graph(
            issues_data=issues_data,
            start_week=start_week,
            end_week=end_week,
            current_year=current_year,
        )

    # --------------------------------------------------------------
    # Create priority levels graph only if PERFORM_PRIORITY_ANALYSIS is true
    if os.getenv("PERFORM_PRIORITY_ANALYSIS", "false").lower() == "true":
        create_issues_score_levels_graph(
            issues_data=issues_data,
            start_week=start_week,
            end_week=end_week,
            current_year=current_year,
        )

    # --------------------------------------------------------------
    # Perform user analysis only if PERFORM_USER_ANALYSIS is true
    if os.getenv("PERFORM_USER_ANALYSIS", "true").lower() == "true":
        # Load excluded users from YAML file
        excluded_users = []
        try:
            import yaml
            with open('configs/exclude_users.yaml', 'r') as file:
                config = yaml.safe_load(file)
                excluded_users = config.get('excluded_users', [])
        except Exception as e:
            print(f"Warning: Could not load excluded users: {str(e)}")

        # Create users directory in tmp
        users_base_path = os.path.join("/workspace/tmp", "users")
        os.makedirs(users_base_path, exist_ok=True)

        # Iterate over the weeks for user analysis
        unique_users = [user for user in get_unique_users_from_issues(issues_data) 
                       if user not in excluded_users]
        
        print("\nUnique active users involved in issues:")
        for user in unique_users:
            print(f"- {user}")
            # Create user-specific directory
            user_path = os.path.join(users_base_path, user)
            os.makedirs(user_path, exist_ok=True)

        # Collect statistics for all users
        users_statistics = []
        
        print("\nCreating graphs for each user:")
        for user in unique_users:
            user_path = os.path.join(users_base_path, user)
            
            # Get weekly issues data for the user
            user_weekly_data = get_user_weekly_issues(
                issues_data=issues_data,
                username=user,
                start_week=start_week,
                end_week=end_week,
                current_year=current_year
            )
            
            # Get weekly scores data for the user
            user_weekly_scores = get_user_weekly_scores(
                issues_data=issues_data,
                username=user,
                start_week=start_week,
                end_week=end_week,
                current_year=current_year
            )
            
            # Collect total statistics for this user
            total_created = sum(week['created_issues'] for week in user_weekly_data)
            total_closed = sum(week['closed_issues'] for week in user_weekly_data)
            total_score = sum(week['open_score'] for week in user_weekly_scores)
            
            users_statistics.append({
                'username': user,
                'open_issues': user_weekly_data[-1]['open_issues'],  # Get only last week's open issues
                'total_score': user_weekly_scores[-1]['open_score']  # Get only last week's score
            })
            
            # Create graph for the user
            create_user_issues_graph(
                user_weekly_data=user_weekly_data,
                username=user,
                save_path=user_path
            )
            
            # Create score graph for the user
            create_user_scores_graph(
                user_weekly_data=user_weekly_scores,
                username=user,
                save_path=user_path
            )
            
            # Add the new priority levels graph
            create_user_priority_levels_graph(
                issues_data=issues_data,
                username=user,
                start_week=start_week,
                end_week=end_week,
                current_year=current_year,
                save_path=user_path
            )
            
            # Print user statistics if logging is enabled
            if os.getenv("PRINT_LOGS_ANALYSIS_RESULTS", "false").lower() == "true":
                print(f"\nWeekly statistics for {user}:")
                headers = ["Week", "Open Issues", "Created", "Closed"]
                table_data = [
                    [
                        week_data['week'],
                        week_data['open_issues'],
                        week_data['created_issues'],
                        week_data['closed_issues']
                    ]
                    for week_data in user_weekly_data
                ]
                print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # --------------------------------------------------------------
    # Create user distribution charts
    create_user_distribution_charts(
        users_statistics=users_statistics,
        end_week=end_week,
        save_path="/workspace/tmp"
    )

    # --------------------------------------------------------------
    # After creating all graphs, merge them into PDF
    create_pdf_report(start_week, end_week)

    # --------------------------------------------------------------
    # Create users PDF report
    create_users_pdf_report(start_week, end_week)


    exit()
