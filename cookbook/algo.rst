LogFlow presentation
====================

Introduction
------------

LogFlow steams from my PhD. It is the conclusion of 3 years of work.
A paper is written and it is submitted. Once it will be accepted, paper will be added to the repository. In this section, we just give a quick overview to help reader to understand LogFlow.
If you need more details, please contact me.

LogFlow is based on the observation that the system logs contain very useful information about the system health but, in the reality, they are not used due the size of the data.
Indeed, a medium HPC system produces more than 2M of lines of logs per day.

Then, we decide to build a system that can help the administrators to use information provided by the logs to maintain the system.
More precisly, by using the power of new AI technics, such as Deep Learning, we want to build a tool that can process very large dataset and that can be able to show the correlations between events to the user.

LogFlow workflow
----------------

To be able to use AI algorithms, a first pre-processing step is needed. Indeed, AI algorithms need numerical values but logs are textual values.
Then, the first step is to turn the textual value into numerical value.

Once this step is done, we can use AI algorithms. Here, we use a LSTM in a generative way. We learn it to predict the next line of logs based on the previous ones.
If it succeeds, we can know that we have correlations between the next line and the previous ones (these correlations are used by the LSTM to predict the next line based on the previous ones).

Then, using these correlations, we build a tree to help users to only focus on relevant correlations by deleting the noise.


State of the art
----------------
Note that LogFlow is not the first work on logs. This field is split into two main parts:
- The log parsing task.
- The model to add value to log.

1) The log parsing task.
The log parsing task aims at answering this question: Do these two papers describe the same event?
Indeed, considering the two following lines:

.. code-block:: bash

    CPU46: Package temperature above threshold
    CPU17: Package temperature above threshold

It is obvious that despite the two lines are differents, they describe the same event: an overheating of the CPU.
Then, we need to build a method to discover these events and to describe these two lines by a pattern:

.. code-block:: bash

    * Package temperature above threshold

When * denotes any word.

We can find several parser in the litterature to solve this issue. Using the survey provided by LogPai (https://github.com/logpai/logparser), we can find at least 13 parsers.
Why develop a new one? Because we are better! (That is not the right answer).
Actually, the best parser of the litterate according to this survey is Drain. But, despite its qualities, it can parse our dataset in less than 41 hours and it cannot parse Thunderbird dataset in less than 48 hours.
We think that this processing time is a major issue in our inter-connected world. Indeed, HPC systems are growing, and users cannot wait entire days to get the parser results.
This is why we develop the parser part of LogFlow. 

2) Adding value to logs.
Most of the work focuses on predicting failures based on logs. We prefer to take another approach: use the knowledge of the administrator instead of replacing it by algorithms.
Why? Because we think that it can be complicated to entierly describe the system to integrate all the knowledge about the system inside a model. Then, we prefer to use the knowledge of the administrator and help him to focus on relevant information.


Main issues solved by LogFlow
------------------------

1) Performance of the log parser.
As we previously explained, actual state-of-the-art parsers fail to parser large dataset in less than 1 day.
To solve this issue, we develop a parser based on two mains ideas:
- Two lines of logs describe the same event if they have the same number of words.
- Fixed part are always at the same place

Using these ideas help us to multithread our algorithm (one thread by size of line) and use a simple algorithm to detect fixed parts: the fixed parts are the most common parts in a log.
Additionally, word descriptors and hashmap are used to better describe the words aand drastically increase the speed of the algorithm.
Namely, we are able to parse Thunderbird and DKRZ dataset in less than 3 minutes!

2) Deduce causal correlations from the LSTM
Unfortunatly, LSTM models are black box models. Then, we cannot know the correlations used by the model to predict the next line of logs.

To solve this first issue, we use an attention layer to get the weight of each input. The more weight, the more impact of the prediction of the LSTM.

3) Without parameters
By design, LogFlow does not require any parameters. You can know forget the tedious task of deriving the optimal parameters from a bunch of boring experiments.

LogFlow algorithm example
=========================

Log parser
----------

Let's start with the following line of logs:

.. code-block:: bash

    1) Temperature_Celsius changed from 55 to 54
    2) Connection of user=R52 from Moon
    3) Temperature_Celsius changed from 54 to 53
    4) Connection of user=B782 from Moon
    5) Connection of user=Felix from Mars

The first step is to describe each word with a descriptor.
Indeed using a strict equality between the words to compare them would be too restrictive. 
If we take two memory addresses, 0x0c35685d and 0x200da20c, with a strict equality, we would simply consider them as different tokens, and so, we may conclude that the token is simply a variable part in alog template. But we think that a more accurate template should consider this token is a memory address.

The descriptors are built using the following rules:
1) For words including only letters, the descriptor is the word itself 
2) For words including only numerical characters, the descriptor is the constant NB
3) For all other words, the descriptor is a vector including 5 entries. The first 4 entries are boolean values
describing the presence of a type of character: numerical characters, uppercase letters, lowercase letters, non alpha-numeric characters. The last entry is the length of the word.

Then, we have:

.. code-block:: bash
    1) (0,1,1,1,19) changed from NB to NB
    2) Connection of user (1,0,1,0,3) from Moon
    3) (0,1,1,1,19) changed from NB to NB
    4) Connection of user (1,0,1,0,4) from Moon
    5) Connection of user Felix from Mars

To find the patterns, we use our simple rule: the fixed parts are the most common parts in a log.
We count the common words with other lines for each line (it uses hashmap in the code to speed up and have a linear complexity instead of quadratic one.)

We have:

1) [1, 1, 1, 1, 1, 1]
2) [2, 2, 2, 0, 2, 1]
3) [1, 1, 1, 1, 1, 1]
4) [2, 2, 2, 0, 2, 1]
5) [2, 2, 2, 0, 2, 0]

For the line 2), the fixed parts are the most common parts in a log. Hence, the common words with 2 other lines. 
For this line, we get "user * from *"


LSTM part
---------
Based on the previous detected pattern, each line is associated with a number (the id of its pattern).
We use word2vec algorithm to turn this id into a numerical vector.

Then, we build a LSTM model following this representation: attention layer => LSTM => Fully connected => Output

The input of the attention layer is the X previous logs turned into numerical vectors. The output is the next log.
Using the weights provided by the attention layer, we can deduce the correlations. 
If the weight is greater than a threshold, then we decide that there is a correlation.

