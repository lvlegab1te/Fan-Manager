import os
from datetime import datetime


class Logger:
    def __init__(self, filePath, fileName, maxFileSize, logsToKeep):
        self._logsToKeep = int(logsToKeep)
        self._maxFileSize = int(maxFileSize)
        self._filePath = filePath
        self._fileName = fileName
        self.logFile = open(f"{self._filePath}{self._fileName}", 'a+')

    def write(self, message, startWith = "datetime",  endWith = "\n"):
        self.CheckFile()

        logline = ""
        if (startWith == "datetime"):
            logline = logline + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + f"{message}"
        elif (startWith == ""):
            logline = message
        else:
            logline = startWith + message

        if (endWith != ""):
            logline = logline + endWith

        self.logFile.write(logline)

        self.logFile.flush()

    def CheckFile(self):
        file_size = os.path.getsize(f"{self._filePath}{self._fileName}")
        if (file_size > (self._maxFileSize * 1024 * 1024)):
            self.logFile.close()
            now = datetime.now()
            formatted_date = now.strftime('%Y%m%d')
            count = 0
            i = self._logsToKeep
            while i > 0:
                if (os.path.exists(f"{self._filePath}{self._fileName}{i}")):
                    if (i == self._logsToKeep):
                        os.remove(f"{self._filePath}{self._fileName}{i}")
                    else:
                        os.rename(f"{self._filePath}{self._fileName}{i}",f"{self._filePath}{self._fileName}{i+1}")
                i = i-1
            
            os.rename(f"{self._filePath}{self._fileName}", f"{self._filePath}{self._fileName}{count+1}")
            logFile = open(f"{self._filePath}{self._fileName}", 'a+')


    def Dispose(self):
        self.logFile.close()