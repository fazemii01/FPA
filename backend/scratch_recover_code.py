import os

def main():
    convo_id = "889d8331-9f92-4723-ab42-73b834bfe900"
    log_path = f"C:\\Users\\fazemii01\\.gemini\\antigravity\\brain\\{convo_id}\\.system_generated\\logs\\transcript_full.jsonl"
    
    if not os.path.exists(log_path):
        print("Log file not found.")
        return
        
    print(f"Searching in current convo full log: {log_path}...")
    
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    pos = content.find("d_pattern_bonus")
    if pos != -1:
        print("\n=== FOUND MATCH ===")
        # Extract 15000 characters to ensure we capture the whole block without truncation
        snippet = content[max(0, pos-2500):pos+9500]
        cleaned = snippet.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
        print(cleaned)
        print("===================\n")
    else:
        print("d_pattern_bonus not found in current full log.")

if __name__ == "__main__":
    main()
