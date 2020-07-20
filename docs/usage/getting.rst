Getting Started
===============

LogFlow aims at processing logs. The first step is to get data to test it.

Data
----

You can find data to test LogFlow on the LogHub repository: https://github.com/logpai/loghub The following example is based on the Windows dataset.

Note that LogFlow is optimized to handle several small files rather than one large file. Then, we can split the Windows dataset into several small files by using split on linux.

Example
-------

According to the three steps process, the example is split into 3 main parts: the logparser, the model and the tree builder.

1) LogFlow import

Start by importing LogFlow

.. code-block:: python3

    from logflow.logsparser.Dataset import Dataset
    from logflow.logsparser.Parser import Parser
    from logflow.logsparser.Embedding import Embedding
    from logflow.logsparser.Journal import Journal

    from logflow.relationsdiscover.Dataset import Dataset as Dataset_learning
    from logflow.relationsdiscover.Worker import Worker

    from logflow.logsparser import Pattern
    from logflow.relationsdiscover import Model
    from logflow.treebuilding.Dataset import Dataset as Dataset_building
    from logflow.treebuilding.Workflow import 

2) Define functions (optional)

We need to define a function to get the message part of one log entry. If this function is not provided, the default behavior is to split the log entry according to the space caractere and keep only the word after the 9th (included)
For the Windows dataset, the message is the words after the 4th word (included)

.. code-block:: python3

    def parser_function(line):
        return line.strip().split()[4:]

If we want to sort the logs according to a field, we can also define a function. For example, using the Windows dataset, we can sort the logs by node.
Note that the logs are sorted per file. LogFlow doesn't sort again the logs per thread. It is a experimental feature, it is better to sort the logs before starting LogFlow.

.. code-block:: python3

    def split_function(line):
        try:
            return line.strip().split()[3]
        except:
            return "1"

3) LogParser

We can start the first module. The first step is to create a dataset. Then, the parser is used to detect the patterns.
A new dataset is created using the previous discovered patterns and embeddings using word2vec are computing according to this new dataset.

.. code-block:: python3

    path_logs = "data/Windows/"
    list_files = []
    for file in listdir(path_logs):
        if "x" in file: # Using split command, each small file begins with a "x"
            list_files.append(path_logs + "/" + file)


    dataset = Dataset(list_files=list_files, parser_function=parser_function) # Generate your data
    patterns = Parser(dataset).detect_pattern() # Detect patterns
    Dataset(list_files=list_files, dict_patterns=patterns, saving=True, path_data="data/", name_dataset="Windows_test", path_model="model/", parser_function=parser_function, sort_function=sort_function) # Apply the detected patterns to the data
    Embedding(loading=True, name_dataset="Windows_test", path_data="data/", path_model="model/").start() # Generate embedding for the LSTM


4) Model

We can learn the corrections based on the previous embeddings. We can set a size to used only 1 000 000 lines for examples. It can speed up the learning process.

.. code-block:: python3

    size=1000000
    list_cardinalities = Dataset_learning(path_model="model/", path_data="data/", name_dataset="Windows_test", size=size).run() # Create your dataset
    worker = Worker(cardinalities_choosen=[4,5,6,7], list_cardinalities=list_cardinalities, path_model="model/", name_dataset="Windows_test") # Create the worker
    worker.train() # Start learning the correlations

5) Tree builder

All is done, we can have the tree representing the correlations.

.. code-block:: python3

    dataset = Dataset_building(path_model="model/", name_model="Windows_test", path_data="data/Windows/Windows.log", parser_function=parser_function) # Build your dataset
    dataset.load_files() # Load the model
    dataset.load_logs() # Load the logs
    workflow = Workflow(dataset) # Build your workflow
    workflow.get_tree(index_line=24712) # Get the tree of the 2338th line

6) Get the results (optional)

To rate our model, we can merge the results of cardinalities. 

.. code-block:: python3

    results = Results(path_model="model/", name_model="Windows_test")
    results.load_files()
    results.compute_results(condition="Test")
    results.print_results()