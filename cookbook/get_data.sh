# Create the data folder
mkdir data

# Create the Thunderbird, Windows et Spark folder
mkdir data/Thunderbird
mkdir data/Windows
mkdir data/Spark

# Download the data
wget https://github.com/bds-ailab/logflow/raw/data/cookbook/data/Spark/Spark.tar.gz
wget https://github.com/bds-ailab/logflow/raw/data/cookbook/data/Thunderbird/Thunderbird.tar.gz
wget https://github.com/bds-ailab/logflow/raw/data/cookbook/data/Windows/Windows.tar.gz

mv Spark.tar.gz data/Spark
mv Windows.tar.gz data/Windows
mv Thunderbird.tar.gz data/Thunderbird

# Uncompress it
tar -xzvf data/Spark/Spark.tar.gz -C data/Spark/
tar -xzvf data/Thunderbird/Thunderbird.tar.gz -C data/Thunderbird/
tar -xzvf data/Windows/Windows.tar.gz -C data/Windows/

# Split it
cd data/Spark/
split -l 100000 Spark.log
cd ../../

cd data/Thunderbird/
split -l 100000 Thunderbird.log
cd ../../

cd data/Windows/
split -l 100000 Windows.log
cd ../../