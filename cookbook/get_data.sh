# Create the data folder
mkdir data

# Create the Thunderbird, Windows et Spark folder
mkdir data/Thunderbird
mkdir data/Windows

# Download the data
wget https://zenodo.org/record/3227177/files/Thunderbird.tar.gz?download=1
wget https://zenodo.org/record/3227177/files/Windows.tar.gz?download=1

mv Windows.tar.gz data/Windows
mv Thunderbird.tar.gz data/Thunderbird

# Uncompress it
tar -xzvf data/Thunderbird/Thunderbird.tar.gz -C data/Thunderbird/
tar -xzvf data/Windows/Windows.tar.gz -C data/Windows/

# Split it
cd data/Thunderbird/
split -l 100000 Thunderbird.log
cd ../../

cd data/Windows/
split -l 100000 Windows.log
cd ../../