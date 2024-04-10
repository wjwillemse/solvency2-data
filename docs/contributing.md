# Contributing

Help us to make this package better. All contributions are welcome and
they are greatly appreciated! Every little bit helps, and credit will
always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at
<https://github.com/wjwillemse/solvency2-data/issues>.

If you are reporting a bug, please include:

-   Your operating system name and version.
-   Any details about your local setup that might be helpful in
    troubleshooting.
-   Detailed steps to reproduce the bug.

### Submit Feedback

The best way to send feedback is to file an issue at
<https://github.com/wjwillemse/solvency2-data/issues>.

If you are proposing a feature:

-   Explain in detail how it would work.
-   Keep the scope as narrow as possible, to make it easier to
    implement.
-   Remember that this is a volunteer-driven project, and that
    contributions are welcome :)

### Development

Clone the package from Github and install with

```shell
poetry install --with dev
```

and set up pre-commit

```shell
pre-commit install
```

To run the tests:

```shell
python -m unittest 
```

To check and format your changes:
```shell
ruff check .   # Lint all files in the current directory.
ruff format .  # Format all files in the current directory.
```

Run pre-commit

```shell
pre-commit run --all-files
``` 

Build the package
```shell
poetry build
``` 

#### Documentation

Install with

```shell
poetry install --with dev
```

Build the documentation
```shell
mkdocs build
``` 

