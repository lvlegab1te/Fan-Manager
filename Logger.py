import os
from datetime import datetime


class Logger:
    def __init__(self, filePath, maxFileSize, logsToKeep):
        global logFile
        global _filePath 
        global _maxFileSize
        _maxFileSize = int(maxFileSize)
        _filePath = filePath
        logFile = open(f"{_filePath}fan-manager.log", 'a+')

    def write(self, message, startWith = "datetime",  endWith = "\n"):
        self.CheckFile()

        logline = ""
        if (startWith == "datetime"):
            logline = logline + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + f" {message}"
        elif (startWith == ""):
            logline = message
        else:
            logline = startWith + message

        if (endWith != ""):
            logline = logline + endWith

        logFile.write(logline)

        logFile.flush()

    def CheckFile(self):
        global logFile
        file_size = os.path.getsize(f"{_filePath}fan-manager.log")
        if (file_size > (_maxFileSize * 1024)):
            logFile.close()
            files = os.listdir(_filePath)
            now = datetime.now()
            formatted_date = now.strftime('%Y%m%d')
            count = 0
            for file in files:
                if file.startswith(f'fan-manager.log{formatted_date}'):
                    count = count + 1
            
            os.rename(f"{_filePath}fan-manager.log", f"{_filePath}fan-manager.log{count+1}")
            logFile = open(f"{_filePath}fan-manager.log", 'a+')


    def Dispose(self):
        logFile.close()