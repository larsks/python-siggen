## Building the documentation

Running `make` will...

- Use [doctest][] to verify the code samples in the documentation.
- Extract the code samples, run them, and generate graphs from the
  results.
- Run the `*.py` scripts that generate the multi-step graphs.
- Render an HTML document from the Markdown sources.

[doctest]: https://docs.python.org/2/library/doctest.html

Use your browser to view the resulting HTML.

## MathJax

This documentation uses [MathJax][] for rendering equations.  Your
browser will need to be able to contact the MathJax servers in order
to properly display the equations.

[mathjax]: https://mathjax.org

