# -----------------------------------------------------------------------------
# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Or your actual UID, GID on Linux if not the default 1000
ARG USERNAME=ada
ARG USER_UID=1005
ARG USER_GID=$USER_UID


# Set environment variables to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive


# Update the system package list and install Python 3, pip, and common dependencies
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    curl \
    # ---------------------------------
    && apt autoremove && apt clean -y \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
RUN \
    # Create a non-root user to use if preferred - see https://aka.ms/vscode-remote/containers/non-root-user.
    groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    # ------------------------------
    # [Optional] Add sudo support for non-root user
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    # ---------------------------------
    && apt autoremove && apt clean -y \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
# Optionally, set Python 3 as the default Python
RUN ln -s /usr/bin/python3 /usr/bin/python

# -----------------------------------------------------------------------------
# Install pip packages
RUN python3 -m pip install --upgrade pip wheel \
    matplotlib \
    pandas \
    numpy \ 
    fpdf \
    requests \
    PyYAML \
    tabulate \
    tqdm \
    --ignore-installed \
    && rm -rf /home/ada/.cache/pip


# -----------------------------------------------------------------------------
# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND= 
CMD ["/bin/bash"]