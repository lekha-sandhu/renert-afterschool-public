# Copyright (C) 2020-2023 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary


class Dictable():
    def toDict(self):
        #from: https://stackoverflow.com/a/50299048
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
