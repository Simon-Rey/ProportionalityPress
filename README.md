# The Proportionality Press

The Proportionality Press is a website developed to demonstrate how the principle of proportionality can be applied to
improve collective decision-making. One key example showcased here is the selection of representative comments
from online discussions. By applying voting rules that respect diverse perspectives, we can identify a set of comments
that best reflect the views of participants — offering a fairer and more informative summary of the conversation.

## Development

This project is structured as a data processing pipeline to generate a static website:

1. **Collect raw data** (currently from Polis polls).
2. **Transform into structured JSON**.
3. **Compute rule results and add analysis**.
4. **Generate a static website**.

Each step produces intermediate outputs (mainly JSON files) so that expensive computations don't need to be repeated.

---

### 1. Data Sources

Currently, the only supported source is **Polis polls** taken from the GitHub repository [Open Polis data](https://github.com/compdemocracy/openData).

* The logic for parsing Polis polls is in `polis.py`.
* A Polis poll is represented as a directory of raw files, which can be read and converted into Python objects.
* Raw polls are converted into JSON files that serve as the standard input for all later stages.

Command to run this step:

```bash
python main.py  # with `all_polis_to_json()` enabled in main()
```

---

### 2. Exploration and Analysis

Core classes used by the website engine are defined in `article.py`:

* **Article**: the central object representing an article of the website.
* **Comment**: a participant's comment to an article.
* **RuleResult**: the output of a voting rule on all the comments of an article.

Workflow:

1. Instantiate the Article class, typically by reading the JSON files produced in step 1.
2. Compute rule results with the tools in `rules.py`. This may take time, so the results should be written back to JSON for reuse.
3. Add analysis metrics with the tools in `analysis.py`.


Typical commands:

```bash
python main.py  # with `compute_and_write_all_rules()` enabled
python main.py  # with `add_analysis_measures()` enabled
```

---

### 3. Website Generation

Once JSON data has been enriched with rule results and analysis, you can build the website.

* `generate.py` handles static site generation.
* It loads Articles from JSON and renders them into HTML.
* Global settings (e.g. layout, configuration) are defined in `settings.py`.
* HTML templates used by the website generator are located in `templates`.
* Static files (CSS, Javascript etc...) are located in `static`. These are automatically copied into the website directory.

Command:

```bash
python main.py  # with `generate_all_polis()` enabled
```
