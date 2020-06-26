# Copyright 2020 BULL SAS All rights reserved #
# import utils
# import time



# ############################################
# ############ Test timing descriptors #######
# ############################################
# if True:
#     begin = time.time()
#     message = ["abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover", "abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover", "abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover"]
#     for i in range(100000):
#         list(map(utils.filter_word, message))
#     print("Timing map: ", time.time() - begin)

#     begin = time.time()
#     message = ["abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover", "abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover", "abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover"]
#     for i in range(100000):
#         y = [utils.filter_word(x) for x in message]
#     print("Timing list: ", time.time() - begin)

#     begin = time.time()
#     message = ["abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover", "abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover", "abc", "abc,", "abc,1", "Abc,1", "123", "123.4", "path/discover"]
#     for i in range(100000):
#         list_tmp = []
#         for x in message:
#             list_tmp.append(utils.filter_word(x))
#     print("Timing for: ", time.time() - begin)

# ############################################
# ############ Test timing comparison ########
# ############################################
# if False:
#     begin = time.time()
#     message = [(1,1,0,1,4), (1,1,0,1,4), (1,1,0,1,4), (1,1,0,1,4), (1,1,0,1,4), (1,1,0,1,4)]
#     for i in range(10000000):
#         for x in message:
#             if x == (1,1,0,1,4):
#                 pass
#     print("Timing set: ", time.time() - begin)

#     begin = time.time()
#     message = [[1,1,0,1,4], [1,1,0,1,4], [1,1,0,1,4], [1,1,0,1,4], [1,1,0,1,4], [1,1,0,1,4]]
#     for i in range(10000000):
#         for x in message:
#             if x == [1,1,0,1,4]:
#                 pass
#     print("Timing list: ", time.time() - begin)

#     begin = time.time()
#     message = ["1,1,0,1,4", "1,1,0,1,4", "1,1,0,1,4", "1,1,0,1,4", "1,1,0,1,4", "1,1,0,1,4"]
#     for i in range(10000000):
#         for x in message:
#             if x == "1,1,0,1,4":
#                 pass
#     print("Timing string: ", time.time() - begin)

#     begin = time.time()
#     message = [11014, 11014, 11014, 11014, 11014, 11014]
#     for i in range(10000000):
#         for x in message:
#             if x == 11014:
#                 pass
#     print("Timing int: ", time.time() - begin)