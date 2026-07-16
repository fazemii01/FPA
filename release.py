import os
import sys
import re
import subprocess

def run_command(cmd, ignore_error=False, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True, cwd=cwd, encoding="utf-8")
        if result.stdout.strip():
            print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(e.stderr.strip())
        if not ignore_error:
            sys.exit(1)
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pubspec_path = os.path.join(script_dir, "mobile", "pubspec.yaml")
    app_info_path = os.path.join(script_dir, "backend", "app", "routers", "app_info.py")

    # 1. Read current version from pubspec.yaml
    if not os.path.exists(pubspec_path):
        print(f"Error: pubspec.yaml not found at {pubspec_path}")
        sys.exit(1)

    with open(pubspec_path, 'r') as f:
        pubspec_content = f.read()

    version_match = re.search(r'^version:\s*([^\s]+)', pubspec_content, re.MULTILINE)
    if not version_match:
        print("Error: Could not find version line in pubspec.yaml")
        sys.exit(1)

    current_version = version_match.group(1)
    print(f"Current version: {current_version}")

    # Parse version name and build code
    if '+' in current_version:
        current_name, current_code_str = current_version.split('+')
        current_code = int(current_code_str)
    else:
        current_name = current_version
        current_code = 1

    # 2. Determine target version name and build code
    if len(sys.argv) > 1:
        # User specified version name (e.g. 1.0.2)
        new_name = sys.argv[1]
        new_code = current_code + 1
    else:
        # Auto-increment patch version
        parts = current_name.split('.')
        if len(parts) >= 3:
            parts[2] = str(int(parts[2]) + 1)
            new_name = '.'.join(parts)
        else:
            new_name = current_name + ".1"
        new_code = current_code + 1

    new_version = f"{new_name}+{new_code}"
    print(f"Target version:  {new_version}")

    # 3. Update pubspec.yaml
    updated_pubspec = re.sub(
        r'^version:\s*([^\s]+)',
        f"version: {new_version}",
        pubspec_content,
        flags=re.MULTILINE
    )
    with open(pubspec_path, 'w') as f:
        f.write(updated_pubspec)
    print("Updated pubspec.yaml successfully.")

    # 4. Update app_info.py
    if not os.path.exists(app_info_path):
        print(f"Error: app_info.py not found at {app_info_path}")
        sys.exit(1)

    with open(app_info_path, 'r') as f:
        app_info_content = f.read()

    updated_app_info = re.sub(
        r'^LATEST_VERSION\s*=\s*["\'][^"\']+["\']',
        f'LATEST_VERSION = "{new_name}"',
        app_info_content,
        flags=re.MULTILINE
    )
    with open(app_info_path, 'w') as f:
        f.write(updated_app_info)
    print("Updated app_info.py successfully.")

    # 4b. Regenerate Flutter Launcher Icons
    print("\n--- Regenerating Flutter Launcher Icons ---")
    mobile_dir = os.path.join(script_dir, "mobile")
    flutter_cmd = "flutter.bat" if os.name == "nt" else "flutter"
    run_command([flutter_cmd, "pub", "get"], cwd=mobile_dir, ignore_error=True)
    run_command([flutter_cmd, "pub", "run", "flutter_launcher_icons"], cwd=mobile_dir, ignore_error=True)

    # 5. Run Git commands
    print("\n--- Running Git commands ---")
    
    # Add files
    run_command(["git", "add", "."])
    
    # Commit
    run_command(["git", "commit", "-m", f"chore(release): bump version to {new_version}"])
    
    # Push main branch
    run_command(["git", "push", "origin", "main"])
    
    # Delete tag locally and on origin if it exists
    run_command(["git", "tag", "-d", f"v{new_name}"], ignore_error=True)
    run_command(["git", "push", "--delete", "origin", f"v{new_name}"], ignore_error=True)
    
    # Create tag
    run_command(["git", "tag", "-a", f"v{new_name}", "-m", f"Release version {new_name}"])
    
    # Push tag
    run_command(["git", "push", "origin", f"v{new_name}"])

    # 6. Visual Verification Check
    print("\n--- Visual Verification Check ---")
    
    def print_check(label, passed=True):
        # Enable ANSI colors on Windows if supported
        if os.name == 'nt':
            os.system('color')
        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"
        symbol = f"{GREEN}✔{RESET}" if passed else f"{RED}✘{RESET}"
        print(f"  [{symbol}] {label}")

    # Check 1: pubspec.yaml updated
    with open(pubspec_path, 'r') as f:
        pub_check = f.read()
    has_pub_ver = f"version: {new_version}" in pub_check
    print_check(f"Version bumped in pubspec.yaml ({new_version})", has_pub_ver)

    # Check 2: app_info.py updated
    with open(app_info_path, 'r') as f:
        api_check = f.read()
    has_api_ver = f'LATEST_VERSION = "{new_name}"' in api_check
    print_check(f"LATEST_VERSION updated in app_info.py ({new_name})", has_api_ver)

    # Check 3: Git tag exists locally
    git_tags = subprocess.run(["git", "tag"], capture_output=True, text=True, encoding="utf-8").stdout
    has_tag = f"v{new_name}" in git_tags.splitlines()
    print_check(f"Git tag v{new_name} created locally", has_tag)

    # Check 4: Git status clean (everything committed)
    git_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, encoding="utf-8").stdout
    is_clean = git_status.strip() == ""
    print_check("Working directory clean (all changes committed)", is_clean)

    print(f"\nSuccess! Released version {new_version} and triggered GitHub Actions build/upload.")

if __name__ == "__main__":
    main()
