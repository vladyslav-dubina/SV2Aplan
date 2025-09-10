import re
import sys


def increment_version(file_path):
    # Template for string "## Version X.YY.ZZ"
    version_pattern = r"(##\s*Version\s+)(\d+)\.(\d+)\.(\d+)"

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    def increase_version(match):
        major = int(match.group(2))  # Major version
        minor = int(match.group(3))  # Minor version
        sub = int(match.group(4))  # Sub Minor version
        sub += 1
        if sub >= 100:
            minor += 1
            sub = 0

        if minor >= 100:
            major += 1
            minor = 0

        return f"{match.group(1)}{major}.{minor}.{sub}"

    updated_content, count = re.subn(version_pattern, increase_version, content)

    if count == 0:
        print("Version string not found!")
        sys.exit(1)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(updated_content)

    print(f"Version incremented in {file_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python increment_version.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    increment_version(file_path)
