DOCS = waveforms.html
EXAMPLES = \
	   example1.svg \
	   example2.svg

IMAGES = \
	 sawtooth-steps.svg \
	 square-steps.svg \
	 triangle-steps.svg \
	 $(EXAMPLES)

%.html: %.md
	python -m doctest $<
	pandoc -c style.css --from=markdown \
	--standalone --to=html5 \
	--mathjax="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML" \
	--highlight-style pygments \
	-fmarkdown-implicit_figures \
	-o $@ $<

%.svg: %.py
	python $<

all: $(DOCS) $(IMAGES)

waveforms.html: $(IMAGES) style.css

$(EXAMPLES): waveforms.md
	python graphex.py -v -W 8 -H 3 $<

clean:
	rm -f $(IMAGES) $(DOCS)
