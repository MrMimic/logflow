
# ################################
# # It's really ugly but needed to be able to load pickle file with Pattern stored inside #
# ################################
# from sys import path, modules
# from os.path import dirname as dir
# path.append(dir(path[0]))
# from logsparser import Pattern
# modules['Pattern'] = Pattern
# ################################
# # export https_proxy=http://129.183.4.13:8080 && export http_proxy=http://129.183.4.13:8080 && pip install cython && pip install loguru word2vec h5py
# from Dataset import Dataset
# from Worker import Worker
# from loguru import logger

# if __name__ == '__main__':
#     size =  300000000 # 100 000 000
#     list_cardinalities = Dataset(path_model="../../model/", path_data="../../data/", name_dataset="DKRZ", size=size).run()
#     worker = Worker(cardinalities_choosen=[4,5,6,7], list_cardinalities=list_cardinalities, path_model="../../model/", name_dataset="DKRZ")
#     worker.train()