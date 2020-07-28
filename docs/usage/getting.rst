Getting Started
===============

The first section describes the way to get the dataset.
The second section shows the classical way to use LogFlow.
The third section gives a complete example. 

Note that more complete explanation can be found on the :ref:`cookbook` section

Data
----

You can find data to test LogFlow on the LogHub repository: https://github.com/logpai/loghub 

The following example is based on the Windows dataset.

Note that LogFlow is optimized to handle several small files rather than one large file. Then, we can split the Windows dataset into several small files by using split on linux.


Workflow
--------

For each new dataset, we always need to do three main steps according to the three steps process:

- Parse the logs
- Learn the correlations
- Show the correlations using a correlations tree

1) Parse the logs

This first step is split into 4 parts. You need to define a function "parser_function" to get the message part of your log (see example "First Example" for example). 

The first part is to read the data and to generate the associated hashmap used by logflow.
Assuming you have a "list_files" variable containing the list of files you want to process, this part is done by:

.. code-block:: python3

    dataset = Dataset(list_files=list_files, parser_function=parser_function) # Generate your data

Next, we can detect the patterns using the previous dataset computed.

.. code-block:: python3

    patterns = Parser(dataset).detect_pattern() # Detect patterns

Then, we can build the dataset using the previous computed patterns. Note, this step write to the disk the dataset used further for the learning step.
This dataset contains the computed patterns and the list of logs replaced by their pattern id.

.. code-block:: python3

    Dataset(list_files=list_files, dict_patterns=patterns, saving=True, path_data="data/", name_dataset="Windows_test", path_model="model/", parser_function=parser_function) # Apply the detected patterns to the data

The last step is to turn this pattern id into numerical vector

.. code-block:: python3

    Embedding(loading=True, name_dataset="Windows_test", path_data="data/", path_model="model/").start() # Generate embedding for the LSTM


2) Learn the correlations

Now, we can use the model based on a LSTM to learn the correlations between our logs.

The first part is to create the dataset per cardinality. For reminder, during the learning step, we have one LSTM model per cardinality to handle the issue of highly imbalanced dataset.

.. code-block:: python3

    list_cardinalities = Dataset_learning(path_model="model/", path_data="data/", name_dataset="Windows_test").run() # Create your dataset
    
Now, we can build our models. Note that you can choose your cardinalties to be learn by setting the cardinalities_choosen parameter.

.. code-block:: python3

    worker = Worker(cardinalities_choosen=[4,5,6,7], list_cardinalities=list_cardinalities, path_model="model/", name_dataset="Windows_test") # Create the worker

The last step is to start the training step. The models are saved automaticaly. The learning step is stopped using a stopping condition: the last increase of the macro-f1 value is lower than 0.01 during 3 consecutives steps.

.. code-block:: python3

    worker.train() # Start learning the correlations

3) Show the correlations tree.

We can used the previous learned model to show the correlations between our logs.

Again, we create our dataset containing our learned model and the patterns discovered during the first step.

.. code-block:: python3

    dataset = Dataset_building(path_model="model/", name_model="Windows_test", path_data="data/Windows/Windows.log", parser_function=parser_function) # Build your dataset

We load the files and the logs

.. code-block:: python3

    dataset.load_files() # Load the model
    dataset.load_logs() # Load the logs

We create our workflow process (a workflow is a complete step including the log parser, the embedding step and the model inference to process raw log).

.. code-block:: python3

    workflow = Workflow(dataset) # Build your workflow

Then, we get the tree!

.. code-block:: python3

        workflow.get_tree(index_line=24712) # Get the tree of the 2338th line


First Example
-------------
A complete example is given here. It is based on main.py provided at the root of the repository.
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

    def sort_function(list_lines):
        return sorted(list_lines, key=lambda line: split_function(line))

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