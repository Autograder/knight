from .time import TimeUtil

# This script refreshes the log file by 'cutting' the first
# third part of it, this script is should be ran by the
# scheduler. There is no way do delete lines in python so
# this script actually stores all the lines needed and rewrites
# them to the log file.
# Author : @mihaivaduva21
# TODO : change paths as on server
with open("/home/wdw/chessboard/project/src/utils/application.log", "r") as f:
    d = f.readlines()

# TODO: Loadtest
with open("/home/wdw/chessboard/project/src/utils/application.log", "w") as f:
    f.write("Last refreshed on :" + str(TimeUtil.get_current_time())+"\n")
    for i in range(len(d)//3, len(d)):
        f.write(d[i])
