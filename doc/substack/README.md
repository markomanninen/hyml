# Article: Letting AI agents write HTML without trusting them

A Substack article about HyML's safe data mode: why rendering the output of AI
agents as HTML is risky, and how HyML compares with HTML sanitizers, with real
Claude agents and for speed.

| File | Contents |
|---|---|
| [hyml_article.md](hyml_article.md) | The article, with its tables as markdown |
| [hyml_article_substack.md](hyml_article_substack.md) | The same article as published on Substack, with the tables as images |
| [article_images/](article_images/) | Header image and the three table images |
| [header_image_prompts.md](header_image_prompts.md) | Prompts used to generate the header image with ChatGPT |
| [make_table_images.py](make_table_images.py) | Renders the table images as HTML pages with HyML's own `render_data`; they were captured from a browser |

The numbers come from [doc/performance.md](../performance.md) and the scripts in
[benchmarks/](../../benchmarks/).
