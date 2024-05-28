from sqlalchemy.orm import class_mapper


class BaseORM:

    def __iter__(self):
        """
        Yield key-value pairs of column names and their values so that dict()
        can easily convert this object to a dictionary.
        """
        for column in class_mapper(self.__class__).columns:
            yield column.key, getattr(self, column.key)
