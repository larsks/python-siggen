DOCS = index.html waveforms.pdf
EXAMPLES = \
	   example1.svg \
	   example2.svg

IMAGES = \
	 sawtooth-steps.svg \
	 square-steps.svg \
	 triangle-steps.svg \
	 $(EXAMPLES)

ifdef PUBLISH
PUBLISHFLAG = -p
endif

ifdef MESSAGE
MESSAGEFLAG = -m "$(MESSAGE)"
endif

%.svg: %.py
	python $<

all: $(DOCS) $(IMAGES)

.PHONY: all

index.html: waveforms.md $(IMAGES) style.css
	python -m doctest $<
	pandoc -c style.css --from=markdown \
	--standalone --to=html5 \
	--mathjax="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-MML-AM_CHTML" \
	--highlight-style pygments \
	-fmarkdown-implicit_figures \
	-o $@ $<

.examples: waveforms.md
	python graphex.py -v -W 8 -H 3 waveforms.md waveform
	touch $@

$(EXAMPLES): waveforms.md .examples

clean:
	rm -f $(IMAGES) $(DOCS) .examples

publish: all
	ghp-import $(PUBLISHFLAG) $(MESSAGEFLAG) -n -f .
