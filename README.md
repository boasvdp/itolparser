# itolparser
Small script to produce iTOL colorstrip metadata files from a table

# Background

iTOL is a web interface to display and manipulate phylogenetic trees, together with metadata. Producing these metadata files can be cumbersome, which is why this script might come in handy.

# Method

itolparser takes a table as input file, and loops through each column. By default, all columns are parsed as categorical. Specific columns can be parsed as continuous by providing a comma-separated list of column names with `--continuous` or ignore columns with `--ignore`.

For categorical columns, colours are selected based on the number of categories in the column. If there are more than 18 values, random colours are generated. Additionally, an annotation file will be created (labeled with `_filtered`) where a maximum number of colours is used, sorted on occurrence (controlled by `--maxcategories`) and uses grey color for other categories. This is e.g. useful for ST typing, which is categorical data often with a lot of different values.

Output files are written to a directory. Parameters such as margin and colorstrip width can be controlled with `--margin` and `--stripwidth` respectively (these can also be changed online in iTOL itself).

# Bugs and suggestions

Create an issue or shoot me an email at boas [dot] vanderputten [at] amsterdamumc [dot] nl
