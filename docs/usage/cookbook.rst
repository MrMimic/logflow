Cookbook
========

To discover LogFlow and its options, several cookbook are available on our Github : https://github.com/bds-ailab/logflow/tree/master/cookbook
First, we begin by giving the list of recipes available. Then, we explain major options.


List of recipes
---------------

Recipes are based on two main dataset Windows and Thunderbird. They should be adapted to work with your dataset.

1) Windows
- total_Windows.py : Complete example on Windows
- sorted_Windows.py : Complete example with logs sorted by nodes.
- multithreading_Windows.py : Complete example while setting the multithreading option.
- one_model_Windows.py : Complete example using only one LSTM model instead of one model per cardinality.
- logpai_Windows.py : Parser example with output set to "logpai" to use the benchmark provided by LogPai.

2) Thunderbird
- total_Thunderbird.py : Complete example on Windows
- sorted_Thunderbird.py : Complete example with logs sorted by nodes.
- multithreading_Thunderbird.py : Complete example while setting the multithreading option.
- one_model_Thunderbird.py : Complete example using only one LSTM model instead of one model per cardinality.
- logpai_Thunderbird.py : Parser example with output set to "logpai" to use the benchmark provided by LogPai.

Major options
-------------
Here, we only focus on the main options of LogFlow.

If you need a complete first example with explanations, go to:
.. getting

1) Split function
By default, LogFlow split the message part of the line after the 9th word. You can provide a function to set another split configuration.

This function takes a line and return the message part.

.. code-block:: python3

    def parser_function(line):
        return line.strip().split()[4:]

Then, you need to provide it each time a dataset is created:

During the reading step
.. code-block:: python3

    dataset = Dataset(list_files=list_files, parser_function=parser_function)

During the parsing step
.. code-block:: python3

    Dataset(list_files=list_files, dict_patterns=patterns, saving=True, path_data="data/", name_dataset="Test", path_model="model/", parser_function=parser_function, sort_function=sort_function, output="logpai") # Write the dataset

During the tree building.
.. code-block:: python3
    
    dataset = Dataset_building(path_model="model/", name_model="Test", path_data="data/Windows/Windows.log", index_line_max=30000, parser_function=parser_function)

2) Sorted option
To increase performance of LogFlow, instead of giving a bunch of logs sorted by timestamp, we can help it by giving logs sorted by nodes for example.
It can reduce the noise, and can help it to learn more reliable correlations.

We need to define a sort function. This function takes a list of lines and return the list of lines sorted.
In this example, we sort the line according the third field.

.. code-block:: python3

    def split_function(line):
        try:
            return line.strip().split()[3]
        except:
            return "1"

    def sort_function(list_lines):
        return sorted(list_lines, key=lambda line: split_function(line))

This function is given when the dataset is computed using the discovered patterns:

.. code-block:: python3
    
    Dataset(list_files=list_files, dict_patterns=patterns, saving=True, path_data="data/", name_dataset="Test", path_model="model/", parser_function=parser_function, sort_function=sort_function)
    
3) Output option
LogFlow is configured to provide internal object to have an automatical workflow by default. But, if you want to integrate the output of the parser (i.e. patterns associated with each line) to another workflow, you can set the output type.
Only one other type is supported for the moment. This type is "logpai". It is used to rate our logparser using the benchmark provided by logpai (https://github.com/logpai/logparser/tree/master/benchmark).

The output is a csv file containing for each line the message ('Content field'), the pattern id ('EventId') and the string representation of the pattern ('EventTemplate').
Please be careful with this option, it can consume a lot of memory. Use only on small files.

4) One model
Instead of building one model per cardinality, we can envision to build one model for all your dataset.
Note that it is not the recommended way due to the highly imbalanced issue associated with logs dataset.

You just need to set one_model=True when building the dataset used for the learning step.

.. code-block:: python3

    list_cardinalities = Dataset_learning(path_model="model/", path_data="data/", name_dataset="Test", one_model=True).run()