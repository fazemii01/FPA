import subprocess

def main():
    try:
        # Search git history for "CLICK FINGER"
        print("Searching git history for 'CLICK FINGER'...")
        result = subprocess.run(
            ["git", "log", "-S", "CLICK FINGER", "--oneline"],
            capture_output=True,
            text=True,
            cwd="e:\\my project\\ALLIA\\FPA"
        )
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        
        # Search git history for "CONSULTING"
        print("\nSearching git history for 'CONSULTING'...")
        result2 = subprocess.run(
            ["git", "log", "-S", "CONSULTING", "--oneline"],
            capture_output=True,
            text=True,
            cwd="e:\\my project\\ALLIA\\FPA"
        )
        print("STDOUT:")
        print(result2.stdout)
        print("STDERR:")
        print(result2.stderr)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
