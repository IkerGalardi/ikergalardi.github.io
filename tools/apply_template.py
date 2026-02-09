import argparse
import sys
from os.path import basename


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


parser = argparse.ArgumentParser()
parser.add_argument("file", help="File to apply the template to", type=str)
parser.add_argument(
    "--type", help="Either 'post', 'post-list' or 'project-list'", type=str
)

args = parser.parse_args()

global_template = open("template/global.html", "r").read()

if args.type == "post":
    post_file = open(args.file, "r+")

    title = basename(args.file)
    post_template = open("template/post.html", "r").read()
    file_contents = post_file.read()
    intermediate = global_template.format(title, post_template)

    post_file.seek(0)
    post_file.truncate(0)
    post_file.write(intermediate.format(file_contents))
elif args.type == "empty":
    post_file = open(args.file, "r+")

    title = basename(args.file)
    file_contents = post_file.read()

    post_file.seek(0)
    post_file.truncate(0)
    post_file.write(global_template.format(title, file_contents))

elif args.type == "post-list":
    eprint("apply_template: 'post-list' currently unsupported")
elif args.type == "project-list":
    eprint("apply_template: 'project-list' currently unsupported")
else:
    eprint(f"apply_template: unknown file type '{args.type}'")
