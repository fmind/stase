# What is STASE ?

_STASE_ provides a set of metrics to describe a dataset of malware labels.

__Goal__:
* evaluate the properties of malware datasets
* identify potential bias in experimental studies
* analyze the decision and classification of antivirus products

# Usage

__Input__: a dataset of labels formatted as a CSV or CSV.GZ file
* columns: antivirus products
* rows: malware files

__Output__: metrics introduce in this research paper (soon to be released)

__Example__:
```
python3 stase.py sample.csv.gz output.json

{
    "equiponderance": 0.2422919148,
    "equiponderance_idx":8.0,
    "exclusivity":0.2626262626,
    "recognition":0.1051423324,
    "synchronicity":0.1677210336,
    "genericity":0.5233236152,
    "uniformity":0.2926562999,
    "uniformity_idx":48.0,
    "divergence":0.7568027211,
    "consensuality":0.2227891156,
    "resemblance":0.6406466991,
    "labels":328.0,
    "apps":99.0,
    "avs":66.0,
}
```

__Technical details__:
* implemented in Python 3 (dependencies in requirements.txt)
* use multiprocessing for performance
* shipped with [Ouroboros](https://github.com/freaxmind/ouroboros) 

# TODO

* Handle more input formats and options

Pull request accepted !
