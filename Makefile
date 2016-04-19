%.css: %.less
	lessc --clean-css --source-map --strict-math=on --strict-units=on $< $@

all: utl_files/static/styles/site.css TAGS

.PHONY: TAGS clean

TAGS:
	etags -R --exclude=data --exclude=demo --exclude=static --exclude='*.min.*' -R

#TODO: target to generate docs

clean:
	rm TAGS utl_files/static/styles/site.css utl_files/static/styles/site.css.map
