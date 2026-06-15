import subprocess

def main():
    try:
        # Run git status
        print("--- GIT STATUS ---")
        res_status = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
            cwd="e:\\my project\\ALLIA\\FPA"
        )
        print(res_status.stdout)
        
        # Run git diff
        print("--- GIT DIFF ---")
        res_diff = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            cwd="e:\\my project\\ALLIA\\FPA"
        )
        print(res_diff.stdout)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
