Welcom to the cooking workshop for LogFlow.

The first thing to do is to download the data using the associated script. 
You will need around 200 Go if you want to be able to play with all the data. Otherwise, you can focus on a small dataset such as Spark or Windows.

```bash
./get_data.sh
```

Next step is to build the docker.

```bash
docker build -t logflow ../.
```

Now, you are ready to parser and learn the correlations.
You will find several scripts for helping you to configure LogFlow according to your wishes.