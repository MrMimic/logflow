Welcom to the cooking workshop for LogFlow.

## Get ready
The first thing to do is to download the data using the associated script. 
You will need around 200 Go if you want to be able to play with all the data. Otherwise, you can focus on a small dataset such as Spark or Windows.

```bash
./get_data.sh
```

Next step is to build the docker.

```bash
docker build -t logflow ../.
```

And then start it

If you want to use nvidia-docker for GPU acceleration, you want use nvidia-docker
```bash
nvidia-docker run -it --pid=host -v $(pwd)/../:/home/code logflow /bin/bash
```

Or you can use classical docker way
```bash
docker run -it --pid=host -v $(pwd)/../:/home/code logflow /bin/bash
```

Once you are inside your docker, if you want to start script from the cookbook directory, you have to adjust your python path:
```bash
export PYTHONPATH=$PYTHONPATH:/home/code
```
Go to the cookbook directory
```bash
cd /home/code/cookbook/
```

Now, you are ready to parser and learn the correlations.
You will find several scripts for helping you to configure LogFlow according to your wishes.

If you just want to test quickly :
```python
python3.6 total_Windows.py
```

Have fun :)

## List of scripts :


- total_Windows.py : Complete example on Windows
- sorted_Windows.py : Complete example with logs sorted by nodes.
- multithreading_Windows.py : Complete example while setting the multithreading option.
- one_model_Windows.py : Complete example using only one LSTM model instead of one model per cardinality.
- logpai_Windows.py : Parser example with output set to "logpai" to use the benchmark provided by LogPai.



## Documentation
More documentation can be found on our readthedoc project: file:///home/marc/Documents/push_test/logflow/docs/_build/html/usage/cookbook.html#list-of-recipes

