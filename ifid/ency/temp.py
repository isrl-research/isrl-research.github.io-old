import os
import re

# This looks for 'github.io/' and captures the character immediately following it
# It uses a negative lookahead (?!ifid/) to make sure we don't double-add the path
pattern = re.compile(r'github\.io/(?!ifid/)([a-zA-Z0-9])')

def insert_path_prefix():
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Inserts 'ifid/ency/' between the slash and the next character
                new_content = pattern.sub(r'github.io/ifid/ency/\1', content)

                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated path in: {path}")

if __name__ == "__main__":
    insert_path_prefix()

