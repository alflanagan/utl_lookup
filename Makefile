DOC_DIR = jsdocs
DOC_CONF = jsdoc.conf
DOC_README = utl_files/static/js/README.md

PYDOC_DIR = doc
PYDOC_CONF = doc/conf.py
PYDOC_MAIN = doc/_build/html/index.html

JS_SOURCES = $(wildcard utl_files/static/js/*.js papers/static/js/*.js)
PY_SOURCES = $(wildcard *.py */*.py */*/*.py */*/*/*.py */*/*/*/*.py)
SH_SOURCES = $(wildcard *.sh)

%.css: %.less
	lessc  --source-map --strict-math=on --strict-units=on $< $@

all: utl_files/static/styles/site.css TAGS $(DOC_DIR)/index.html

.PHONY: clean

TAGS: $(JS_SOURCES) $(PY_SOURCES) $(SH_SOURCES)
	etags -R --exclude=data --exclude=static --exclude='*.min.*' --exclude=$(DOC_DIR) --exclude='*.json'

clean:
	rm -f TAGS utl_files/static/styles/site.css utl_files/static/styles/site.css.map; \
	if [ ! -z '$(DOC_DIR)' ]; then \
	   rm -f $(DOC_DIR)/*.html; \
	   rm -f $(DOC_DIR)/*.css; \
	   rm -rf $(DOC_DIR)/fonts $(DOC_DIR)/scripts $(DOC_DIR)/styles; \
	fi

# protect against case where DOC_DIR not defined and rm -f $(DOC_DIR)/* ==> rm -f /*
# not that that ever happend to me of course
$(DOC_DIR)/index.html: $(JS_SOURCES) $(DOC_CONF) $(DOC_README)
	if [ ! -z '$(DOC_DIR)' ]; then \
	   rm -f $(DOC_DIR)/*.html; \
	   rm -f $(DOC_DIR)/*.css; \
	   rm -rf $(DOC_DIR)/fonts $(DOC_DIR)/scripts $(DOC_DIR)/styles; \
	fi; \
	jsdoc -c $(DOC_CONF) -a all --verbose $(JS_SOURCES)

$(PYDOC_MAIN): $(PY_SOURCES) $(PYDOC_CONF) $(PYDOC_DIR)/*.rst
	rm -r doc/_build/* doc/api/* doc/management/*; \
	cd doc; \
	$(MAKE) clean; \
	$(MAKE) html

.PHONY: jsdocs
jsdocs: $(DOC_DIR)/index.html ;

.PHONY: pydocs
pydocs: $(PYDOC_MAIN) ;

.PHONY: docs
docs: jsdocs pydocs ;
