# ACHE focused crawler

## Introduction

ACHE is an implementation of a focused crawler. A focused crawler is a web crawler that collects Web pages that satisfy
some specific property, by carefully prioritizing the crawl frontier and managing the hyperlink exploration process [1].

## Installation

### Download with Conda

You can download `ache` from Binstar [2] with Conda [3] by running:

```bash
  conda install -c memex ache
```

### Build from source with Gradle

To build `ache` from source, you can run the following commands in your terminal:

```bash
  git clone https://github.com/chdoig/ache.git
  cd ache
  ./gradlew clean installApp
```

which will generate an installation package under `/build/install/`.

Alternatively, you can build a zip archive:

```bash
  git clone https://github.com/chdoig/ache.git
  cd ache
  ./gradlew clean distZip
```

which will generate a zip file of your project under `/build/distributions/`.

Learn more about Gradle: [http://www.gradle.org/documentation](http://www.gradle.org/documentation).


## Running

### Building a model

To run the ache crawler, you'll first need to build a model.

```bash
$ ache buildModel <target storage config path> <training data path> <output path>
```

`<target storage config path>` is the path to the configuration of the target storage.

`<training_data>` is the path to the directory containing positive and negative examples.

`<output path>` is the new directory where you want to save the generated model files: pageclassifier.model and
pageclassifier.features.

For example:

```bash
ache buildModel conf/sample_crawl/target_storage.cfg training_data models/sample_model/
```


### Running a crawl

To start a crawl, run:

```bash
ache startCrawl <data output path> <config path> <seed path> <model path> <lang detect profile path>
```
`<data output path>` is the path to the directory you want to store your output.

`<config path>` is the path to the config directory.

`<seed path>` is the path to the seed list file.

`<model path>` is the path to the model directory (containing pageclassifier.model and pageclassifier.features).

`<lang detect profile path>` is the path to the language detection profile. Note: We are currently refactoring the code.
You'll be able to find it under resources in the near future. You can currently download here:
[https://code.google.com/p/language-detection/wiki/Downloads](https://code.google.com/p/language-detection/wiki/Downloads).

For example,

```bash
$ ache startCrawl sample_crawl conf/sample_config seeds/sample_crawl.seeds models/sample_model/ libs/profiles/
```

## Requirements

To use ache, you'll need the following:

- JDK 1.6+


[1]: http://en.wikipedia.org/wiki/Focused_crawler
[2]: https://binstar.org/
[3]: http://conda.pydata.org/
