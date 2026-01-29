HTML_PAGES=build/posts/2021-11-04-journey-to-first-completed-project.html \
		   build/posts/2021-11-30-rendering-adventures.html \
		   build/posts/2022-03-08-thought-about-the-linux-desktop.html \
		   build/posts/2022-09-26-how-not-to-write-performant-code.html \
		   build/posts/2022-11-16-data-object-oriented-game.html \
		   build/posts/2023-01-31-exceptional-error-handling.html \
		   build/posts/2023-12-13-everything-is-a-file.html \
		   build/posts/2024-07-17-how-cat-works.html

all: $(HTML_PAGES)

build/posts/%.html: posts/%.md
	python3 tools/remove_md_tags.py $< | cmark --to html > $@
	python3 tools/apply_template.py --type post $@

clean:
	rm -rf build/posts/*.html
