import os
from .base import Hook

class CSVExporter(Hook):
    """ Export training statistics to csv file
    """

    def __init__(self, output, append=False, columns=None):
        """ Constructor

        Arguemnts:
            output (str): Name of csv file to export
            append (bool): Append to file instead of overwriting it
            columns (list): List of columns name to export. If is none select
            to display all columns (default)
        """
        self.output = output
        self.append = append
        self.columns = columns

    def pre_training(self):
        if self.columns is None:
            self.columns = ['epoch', 'step'] + self.trainer.meters_names()

        if os.path.isfile(self.output) and self.append:
            new_file = True
            mode = 'a+'
        else:
            new_file= False
            mode = 'w+'

        self.file_handle = open(self.output, mode)

        if not new_file:
            self.file_handle.write(','.join(self.columns))

    def log(self):
        stats = self.trainer.last_stats
        stats.update({'epoch': self.trainer.epochs_trained,
                      'step': self.trainer.step})

        new_row = (stats.get(column, '') for column in self.columns)

        self.file_handle.write(os.linesep + ','.join(map(str, new_row)))
        self.file_handle.flush()

    def post_training(self):
        self.file_handle.close()