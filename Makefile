DOC_DIR=jsdocs

%.css: %.less
	lessc --clean-css --source-map --strict-math=on --strict-units=on $< $@

all: utl_files/static/styles/site.css TAGS docs

.PHONY: TAGS clean docs

TAGS:
	etags -R --exclude=data --exclude=demo --exclude=static --exclude='*.min.*' --exclude=$(DOC_DIR) -R

#TODO: target to generate docs

clean:
	rm -f TAGS utl_files/static/styles/site.css utl_files/static/styles/site.css.map
	if [ ! -z '$(DOC_DIR)' ]; then rm -rf $(DOC_DIR)/*; fi

docs:
	jsdoc -c jsdoc.conf -a all --verbose utl_files/static/js/utl_files.js
