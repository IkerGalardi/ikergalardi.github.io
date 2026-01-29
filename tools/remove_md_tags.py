import sys

md_lines = open(sys.argv[1]).readlines()

num_slashes = 0
for line in md_lines:
    if num_slashes >= 2:
        print(line.replace("\n", ""))

    if line.strip() == "---":
        num_slashes += 1
