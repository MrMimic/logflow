[![Inline docs](https://img.shields.io/badge/license-GPL-success)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Workflow status](https://github.com/bds-ailab/logflow/workflows/Python_tests/badge.svg)](https://github.com/bds-ailab/logflow/actions?query=workflow%3APython_tests)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=bds-ailab_logflow&metric=alert_status)](https://sonarcloud.io/dashboard?id=bds-ailab_logflow)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=bds-ailab_logflow&metric=ncloc)](https://sonarcloud.io/dashboard?id=bds-ailab_logflow)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=bds-ailab_logflow&metric=bugs)](https://sonarcloud.io/dashboard?id=bds-ailab_logflow)


# LogFlow

## In a nutshell.
LogFlow provides a tool to automate the logs analysis task. This analysis provides the correlations between the logs to help users to understand this amount of data.
LogFlow is split into 3 modules: the log parsing tool, the relations discover model and the tree building tool.

### Log parsing
The log parsing too aims at finding the pattern corresponding to a line of log to be able to extract value from this line. 
More precisely, each line is associated with a pattern. A pattern is a set of fixed words corresponding to the fixed parts of the line (the variable parts are removed).

Using the line "Connexion of user Marc", we can see that "Marc" is the variable part and "Connexion of user" is the fixed part. Then, the associated pattern is "Connexion of user *".

### Relations discover
Once these patterns are associated, the relations between them can be learned. A relation can be the relation between network timeout and a failure for example.
Our model is based on a LSTM augmented with an Attention layer to be able to learn and to analyse the correlations.

### Tree building tool.
The correlation tree can be learned based on the previous learned correlation. The tree shows the user the correlation in a compact view to help him to detect relevant information from its logs.

## Major concepts
To be able to use LogFlow, several concepts need to be explained.

### General
LogFlow is designed to handle large and very large datasets (from 10 million of lines to several billions of lines), then ideas and concepts used to its implementation follow this need of performance for large data.

The log parsing tool can be used with a dataset of any size but the relation discover model should be use only with a large dataset (more than 10 millions of lines) because it relies on deep learning model.

### Log parsing
The log parsing tool relies on one major concept to work: the pattern detection is done only between lines with same sizes.
#### Message length
The size of a line is defined as a number of words. The line is split according to the three letters: " " (whitespace), ":" and "=".
Once the list is split, the pattern detection is done using the best common subsequence with the other lines.

In other word, the pattern is defined as the maximum number of common words between lines. 
#### Multithreading
To enable multithreading, patterns corresponding to each size of line are computed into one thread. Then, it's impossible to have the same pattern for two lines with different number of words.
### Relations discover
To be able to deal with unbalanced number of events, the relations discover uses a simple method: each cardinality of an event is associated with one model (one model = LSTM + Attention layer).
A cardinality is defined as the ten power number of lines associated to the pattern. Then, a cardinality of 4 means that the pattern is associated with 10000 lines.

Then, one model learns the correlations of the patterns with the same cardinality.
Basically, for a large dataset, cardinality varies between 0 and 8.

Note that due to the use of deep learning model, lower cardinality (i.e. lower than 4) should be ignored during the training step.


## Installation
LogFlow can be installed using pip or docker. The recommended way is to use docker.

Note that we will need *nvidia-docker* if you want to use GPU acceleration for the LSTM learning task.

### Docker
Using the Dockerfile at the root of this git.

```bash
docker build -t logflow .
```

Then, start the docker using nvidia-docker
```bash
nvidia-docker run -it --pid=host -v $(pwd):/home/code logflow /bin/bash
```

Now, you are inside your docker
```bash
cd /home/code
```

Create a data and a model directory
```bash
mkdir data
mkdir model
```

Now, you are ready !

### Pip

```bash
pip install -i https://test.pypi.org/simple/ --no-cache-dir --extra-index-url=https://pypi.org/simple/ LogFlow-Atos-Marc-Platini
```

Note that it's a pre-alpha pip version. Prefer to use Docker installation instead of pip.

## Getting Started

### Data
You can find data to test LogFlow on the LogHub repository: https://github.com/logpai/loghub
The following example is based on the *Windows* dataset.

Note that LogFlow is optimized to handle several small files rather than one large file. Then, we can split the Windows dataset into several small files by using *split* on linux.

### Example
A main.py is provided as example.

First, import logflow
```python
from logflow.logsparser.Dataset import Dataset
from logflow.logsparser.Parser import Parser
from logflow.logsparser.Embedding import Embedding
from logflow.logsparser.Journal import Journal

from logflow.relationsdiscover.Dataset import Dataset as Dataset_learning
from logflow.relationsdiscover.Worker import Worker

from logflow.logsparser import Pattern
from logflow.relationsdiscover import Model
from logflow.treebuilding.Dataset import Dataset as Dataset_building
from logflow.treebuilding.Workflow import Workflow

```
First, we need to define the function to get the message part of one line of log.

```python
def parser_function(line):
    return line.strip().split()[4:]
```

Additionally, if we want to sort the logs according to a field, we can use a specific function
```python
def split_function(line):
    try:
        return line.strip().split()[3]
    except:
        return "1"
```


We can start with the first module: the logparsing tool.

```python
path_logs = "data/Windows/"
list_files = []
for file in listdir(path_logs):
    if "x" in file: # Using split command, each small file begins with a "x"
        list_files.append(path_logs + "/" + file)


dataset = Dataset(list_files=list_files, parser_function=parser_function) # Generate your data
patterns = Parser(dataset).detect_pattern() # Detect patterns
Dataset(list_files=list_files, dict_patterns=patterns, saving=True, path_data="data/", name_dataset="Windows_test", path_model="model/", parser_function=parser_function, sort_function=sort_function) # Apply the detected patterns to the data
Embedding(loading=True, name_dataset="Windows_test", path_data="data/", path_model="model/").start() # Generate embedding for the LSTM
```

Now, we can learn the correlations
```python
size=1000000
list_cardinalities = Dataset_learning(path_model="model/", path_data="data/", name_dataset="Windows_test", size=size).run() # Create your dataset
worker = Worker(cardinalities_choosen=[4,5,6,7], list_cardinalities=list_cardinalities, path_model="model/", name_dataset="Windows_test") # Create the worker
worker.train() # Start learning the correlations
```

Additionally, we can have the merged results to compare our results.

```python
results = Results(path_model="model/", name_model="Windows_test")
results.load_files()
results.compute_results(condition="Test")
results.print_results()
```  

At the end, we can get the correlations tree.

```python
dataset = Dataset_building(path_model="model/", name_model="Windows_test", path_data="data/Windows/Windows.log", parser_function=parser_function) # Build your dataset
dataset.load_files() # Load the model
dataset.load_logs() # Load the logs
workflow = Workflow(dataset) # Build your workflow
workflow.get_tree(index_line=24712) # Get the tree of the 2338th line
```

That's it.

### Important parameters
*path_data* and *path_model* is the path to your directory of data and models.

*size* is the size of your data for the learning step. 

*cardinalities_choosen* is the cardinalities used for the learning. Other cardinalities are excluded.

## Documentation
https://logflow.readthedocs.io/en/latest/

## Contact
marc.platini@gmail.com

