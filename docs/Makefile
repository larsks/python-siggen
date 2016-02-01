DOCS = sawtooth.html
IMAGES = sawtooth-steps.svg example1.svg

%.html: %.md
	pandoc -c style.css --from=markdown \
	--standalone --to=html5 \
	--mathjax="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML" \
	--highlight-style pygments \
	-fmarkdown-implicit_figures \
	-o $@ $<

%.svg: %.py
	python $<

all: $(DOCS) $(IMAGES)

sawtooth.html: sawtooth-steps.svg style.css

clean:
	rm -f $(IMAGES) $(DOCS)
