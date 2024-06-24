#!/bin/sh

REPO_DIR="$HOME/.workshop4-repo"
WORKSPACE_DIR="$HOME/workspace"
VENV_DIR="$WORKSPACE_DIR/.venv"

msg() {
    printf "\e[1;32m%s\e[0m\n" "$1"
}

# Truncation guard
if true; then
    set -eu

    # Cleaning up existing directories
    rm -rf "${REPO_DIR}" "${VENV_DIR}"

    msg "System setup"
    sudo tee /boot/os_config.json > /dev/null <<EOF
{
    "keyboard": "us",
    "language": "en"
}
EOF
    sudo raspi-config --apply-os-config

    msg "Enable OpenSSH"
    sudo sed -E -i 's|^#?(PasswordAuthentication)\s.*|\1 no|' /etc/ssh/sshd_config
    sudo systemctl enable --now ssh
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    cat > ~/.ssh/authorized_keys << EOF
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJUTNpJ+H7IAsv2k/4sdLWH63HIqkHny/8ynpHLQ5f5B cuih7@apple.i.cvhc.cc
EOF

    msg "Installing system dependencies"
    sudo apt-get -qq update
    sudo apt-get -qq install -y portaudio19-dev libttspico-utils vim
    sudo apt-get -qq purge -y geany geany-common

    msg "Creating the workspace directory"
    mkdir -p "${WORKSPACE_DIR}"
    # Bookmark in the file manager
    mkdir -p ~/.config/gtk-3.0/
    echo "file://$HOME/workspace" > ~/.config/gtk-3.0/bookmarks

    msg "Setup Desktop"
    # Link on the Desktop
    ln -srnf "${WORKSPACE_DIR}" "$(xdg-user-dir DESKTOP)/workspace"
    cat > "$(xdg-user-dir DESKTOP)/Student Agenda.desktop" << EOF
[Desktop Entry]
Encoding=UTF-8
Name=Student Agenda
Type=Link
URL=https://docs.google.com/spreadsheets/d/1cvTw__4IYjAAXyNV2AAKqFVu-SKLHfNIz5p-gb0Ye90/preview
Icon=text-html
EOF
    cat > "$(xdg-user-dir DESKTOP)/ProperData ChatGPT.desktop" << EOF
[Desktop Entry]
Encoding=UTF-8
Name=ProperData ChatGPT
Type=Link
URL=https://chatgpt.properdata.org/
Icon=text-html
EOF

    msg "Cloning the code repo"
    git clone --quiet https://github.com/UCI-Networking-Group/ProperData_workshop4.git "${REPO_DIR}"
    ln -srf "${REPO_DIR}/voice_assistant_lib.py" "${WORKSPACE_DIR}/"
    ln -srf "${REPO_DIR}/extra_functions.py" "${WORKSPACE_DIR}/"

    msg "Setting up Python environment"
    python -m venv "${VENV_DIR}"
    ln -srf "${REPO_DIR}/voice_assistant_lib.py" "${VENV_DIR}/lib/python3.11/site-packages"
    ln -srf "${REPO_DIR}/extra_functions.py" "${VENV_DIR}/lib/python3.11/site-packages"
    . "${VENV_DIR}/bin/activate"
    pip install -r "${REPO_DIR}/requirements.txt"
    sed -i '/### For workshop/d' ~/.bashrc
    echo "source ${VENV_DIR}/bin/activate  ### For workshop" >> ~/.bashrc

    # Thonny configuration
    xdg-mime default org.thonny.Thonny.desktop text/x-python
    mkdir -p ~/.config/Thonny/
    cat > ~/.config/Thonny/configuration.ini << EOF
[general]
configuration_creation_timestamp = 2024-06-18T00:08:36.002319
language = en_US
environment = []
single_instance = True
event_logging = False
disable_notification_sound = False
debug_mode = False
ui_mode = simple
scaling = default
font_scaling_mode = default

[view]
full_screen = False
maximize_view = False
ui_theme = Raspberry Pi
shellview.visible = True
show_program_arguments = False
show_plotter = False
assistantview.visible = False
astview.visible = False
stackview.visible = False
exceptionview.visible = False
filesview.visible = False
heapview.visible = False
helpview.visible = False
notesview.visible = False
objectinspector.visible = False
outlineview.visible = False
todoview.visible = False
variablesview.visible = False
name_highlighting = True
locals_highlighting = False
paren_highlighting = True
syntax_coloring = True
highlight_tabs = True
highlight_current_line = False
show_line_numbers = True
recommended_line_length = 0

[LocalCPython]
last_configurations = [{'run.backend_name': 'LocalCPython', 'LocalCPython.executable': '$HOME/workspace/.venv/bin/python'}, {'run.backend_name': 'LocalCPython', 'LocalCPython.executable': '/usr/bin/python3'}]
executable = $HOME/workspace/.venv/bin/python

[run]
backend_name = LocalCPython
program_arguments =
dock_user_windows = False
pgzero_mode = False
allow_running_unnamed_programs = True
auto_cd = True
warn_module_shadowing = False
birdseye_port = 7777
run_in_terminal_python_repl = False
run_in_terminal_keep_open = True
working_directory = $HOME/workspace/

[assistance]
disabled_checks = []
open_assistant_on_errors = True
open_assistant_on_warnings = False
use_pylint = True
use_mypy = True

[layout]
zoomed = False
notebook_nw_visible_view = None
notebook_w_visible_view = None
notebook_sw_visible_view = None
notebook_s_visible_view = ShellView
notebook_ne_visible_view = None
notebook_e_visible_view = None
notebook_se_visible_view = None
width = 1130
height = 700
left = 150
top = 50
west_pw_width = 210
east_pw_width = 210
nw_nb_height = 210
sw_nb_height = 210
s_nb_height = 210
se_nb_height = 210
ne_nb_height = 210

[file]
current_file = None
open_files = []
reopen_all_files = False
avoid_zenity = False
make_saved_shebang_scripts_executable = True

[edit]
automatic_calltips = False
automatic_completions = False
automatic_completion_details = True
tab_request_completions_in_editors = False
tab_request_completions_in_shell = True
indent_with_tabs = False

[debugger]
frames_in_separate_windows = False
automatic_stack_view = True
allow_stepping_into_libraries = False
preferred_debugger = faster

[shell]
clear_for_new_process = True
tty_mode = True
max_lines = 1000
squeeze_threshold = 1000
auto_inspect_values = True
EOF

    cd /tmp
    python -c 'from voice_assistant_lib import *; init_voice_assistant(); play(text_to_speech("Set up completed!", "pico"))'

    msg "Done!"
fi
