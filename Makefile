DOC_DIR=jsdocs

%.css: %.less
	lessc --clean-css --source-map --strict-math=on --strict-units=on $< $@

all: utl_files/static/styles/site.css TAGS docs

.PHONY: TAGS clean docs

TAGS:
	etags -R --exclude=data --exclude=demo --exclude=static --exclude='*.min.*' --exclude=$(DOC_DIR) -R

clean:
	rm -f TAGS utl_files/static/styles/site.css utl_files/static/styles/site.css.map
	if [ ! -z '$(DOC_DIR)' ]; then \
	   rm -f $(DOC_DIR)/*.html; \
	   rm -f $(DOC_DIR)/*.css; \
	   rm -rf $(DOC_DIR)/fonts $(DOC_DIR)/scripts $(DOC_DIR)/styles; \
	fi

docs:
	if [ ! -z '$(DOC_DIR)' ]; then \
	   rm -f $(DOC_DIR)/*.html; \
	   rm -f $(DOC_DIR)/*.css; \
	   rm -rf $(DOC_DIR)/fonts $(DOC_DIR)/scripts $(DOC_DIR)/styles; \
	fi
	jsdoc -c jsdoc.conf -a all --verbose utl_files/static/js/utl_files.js
