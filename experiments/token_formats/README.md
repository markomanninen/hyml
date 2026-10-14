# Page elements as model input: five formats

Skyvern [measured](https://www.skyvern.com/blog/html-vs-json-llm-tokens-cost-reduction-success-rate/)
that describing a page's interactive elements to a browser agent's model as
HTML takes fewer tokens than JSON. This measures whether HyML notation would
take fewer still.

Run on 13 October 2026 with three saved pages: the English Wikipedia article
on Lisp (1,412 elements), the Hacker News front page (230) and GitHub's login
page (19). Python.org and PyPI served bot-check pages and were skipped.

| Format | Tokens (o200k) | Tokens (cl100k) | Relative to HTML |
|---|---:|---:|---:|
| HTML | 51,950 | 52,034 | 1.00 |
| HyML s-expression | 53,995 | 54,083 | 1.04 |
| HyML JSON | 62,015 | 62,103 | 1.19 |
| JSON, compact | 78,730 | 77,157 | 1.52 |
| JSON, indented | 99,246 | 97,673 | 1.91 |

HyML s-expressions are about as compact as HTML but not more compact. The
closing parenthesis saves the closing tag, and the quotes around every text
and value and the colon before every attribute name cost it back. Claude's
tokenizer is not available offline, so these counts are a proxy for Claude.
