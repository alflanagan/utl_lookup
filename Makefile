all: utl_lookup/static/css/site.css

%.css: %.less
	lessc --clean-css --source-map --strict-math=on --strict-units=on $< $@
