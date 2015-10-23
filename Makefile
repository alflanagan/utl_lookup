%.css: %.less
	lessc --clean-css --source-map --strict-math=on --strict-units=on $< $@

all: utl_files/static/styles/site.css
