import os
from datetime import date


class PostMetadata:
    def __init__(self, publication: date, title: str, first_paragraph: str):
        self.publication = publication
        self.title = title
        self.first_paragraph = first_paragraph

    def __lt__(self, other):
        return self.publication < other.publication


def print_metadata(metadata: PostMetadata) -> None:
    print(f"Post '{metadata.title}' published on {metadata.publication}'")


def extract_metadata_line(line: str) -> tuple[str, str]:
    parts = line.strip().split(":")
    return (parts[0], parts[1].strip())


def extract_metadata(file: str) -> PostMetadata:
    PRE_TRIPLE_SLASH = 0
    META = 2
    POST = 4

    title: str | None = None
    publication: date | None = None
    first_paragraph: str | None = None

    state = PRE_TRIPLE_SLASH
    lines = open(file, "r").readlines()
    for line in lines:
        line = line[:-1]
        if state == PRE_TRIPLE_SLASH:
            if line == "---":
                state = META
        elif state == META:
            if line == "---":
                state = POST
            else:
                type, value = extract_metadata_line(line)
                if type == "title":
                    title = value
                elif type == "date":
                    date_splited = value.split("-")
                    publication = date(
                        int(date_splited[0]), int(date_splited[1]), int(date_splited[2])
                    )
        elif state == POST:
            if len(line) > 0 and line[0] != "#":
                first_paragraph = line.strip()
                break

    assert title is not None
    assert publication is not None
    assert first_paragraph is not None

    return PostMetadata(publication, title, first_paragraph)


posts_metadata = []
directory = os.fsencode("posts")
for filename in os.listdir(directory):
    metadata = extract_metadata("posts/" + filename.decode())
    posts_metadata.append(metadata)

posts_metadata.sort(reverse=True)


global_template = open("template/global.html", "r").read()
post_template = open("template/post_miniature.html", "r").read()

post_list_html: str = ""
for post in posts_metadata:
    post_html = post_template.format(post.title, post.first_paragraph, post.publication)
    post_list_html += post_html + "\n"

print(global_template.format("Iker Galardi - Posts", post_list_html))
