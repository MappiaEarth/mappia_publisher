import os

class FeedbackWrapper:
    def __init__(self):
        self.console_info = []
        self.progress = 0
        self.progress_text = ""
        self.canceled = False

    def pushConsoleInfo(self, message):
        """Appends a message to the console info array."""
        # self.console_info.append(message)
        print("Push: " + message)


    def setProgress(self, progress):
        """Sets the progress value."""
        self.progress = progress

    def setProgressText(self, text):
        """Sets the progress text."""
        self.progress_text = text

    def isCanceled(self):
        """Returns whether the process is canceled."""
        return self.canceled

    def cancel(self):
        """Cancels the process."""
        self.canceled = True

    def getConsoleInfo(self):
        """Returns all console info messages."""
        return self.console_info

    def printConsoleInfo(self):
        """Prints all console info messages."""
        for message in self.console_info:
            print("Print: " + message)
