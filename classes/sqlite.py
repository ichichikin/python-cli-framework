from classes.utils import Utils
from system.config import Config
import sqlite3
import os
import time
from typing import List, Union, Any, Dict
from classes.log import Log


class Sqlite:
    def __init__(self, database: str, column_types: List[str], column_names: List[str] = None, table: str = None, wait_if_locked: bool = True, timeout: int = 10):
        assert column_names is None or len(column_names) == len(column_types), "Count of column names must be equal to count of column types"

        if database.endswith(".sqlite3"):
            self.__path = database
        else:
            self.__path = Utils.get_absolute_path("data", database.lower() + ".sqlite3")
        self.__connection = sqlite3.connect(self.__path, timeout=timeout)
        self.__cursor = self.__connection.cursor()
        self.__wait_if_locked = wait_if_locked

        column_types = [c.lower() for c in column_types]
        self.__table = table
        if self.__table is None:
            if column_names is None:
                self.__table = "table_" + hex(int.from_bytes(str(column_types).lower().encode("UTF-8"), byteorder='big', signed=False))[2:][-20:]
            else:
                self.__table = "table_" + hex(int.from_bytes(str(column_names + column_types).lower().encode("UTF-8"), byteorder='big', signed=False))[2:][-20:]

        if column_names is None:
            self.__column_names = []
            for i, c in enumerate(column_types):
                self.__column_names.append("column_" + str(i))
        else:
            self.__column_names = [c.lower() for c in column_names]

        columns = [" ".join(c) for c in zip(self.__column_names, column_types)]

        self.__execute("PRAGMA max_page_count = " + str(1073741823 * 5))  # 5TB
        self.__execute("PRAGMA temp_store_directory = '" + Utils.get_absolute_path("data") + "'")
        self.__execute("CREATE TABLE IF NOT EXISTS " + self.__table + " (" + ", ".join(columns) + ")")

    def manual_commit(self) -> None:
        assert self.__connection, "No connection to database"

        self.__connection.commit()

    def drop_and_disconnect(self, table: str = None) -> None:
        assert self.__connection, "No connection to database"

        if table:
            self.__execute("DROP TABLE " + self.__table)
            self.__connection.commit()
            self.__execute("VACUUM")
            self.__connection.commit()

        self.close()

        if not table:
            os.remove(self.__path)

    def truncate(self) -> None:
        assert self.__connection, "No connection to database"

        self.__execute("DELETE FROM " + self.__table)
        self.__connection.commit()
        self.__execute("VACUUM")
        self.__connection.commit()

    def manual_query(self, query: str) -> sqlite3.Cursor:
        assert self.__connection, "No connection to database"

        return self.__execute(query)

    def get_table_name(self) -> str:
        assert self.__connection, "No connection to database"

        return self.__table

    def get_column_names(self) -> List[str]:
        assert self.__connection, "No connection to database"

        return self.__column_names

    def write(self, data: Union[List[List[Any]], List[Any], List[Dict[str, Any]], Dict[str, Any]]) -> sqlite3.Cursor:
        assert self.__connection, "No connection to database"

        if isinstance(data, list) and len(data):
            if isinstance(data[0], list) or isinstance(data[0], tuple):
                for d in data:
                    assert len(self.__column_names) == len(d), "Count of column names must be equal to count of data list"
                return self.__executemany("INSERT INTO " + self.__table + "(" + ", ".join(self.__column_names) + ") VALUES (" + ", ".join(["?"] * len(self.__column_names)) + ")", data)
            elif isinstance(data[0], dict):
                __data = []
                for d in data:
                    __list = []
                    for c in self.__column_names:
                        for k, v in d.items():
                            if c == k:
                                __list.append(v)
                                break
                    assert len(self.__column_names) == len(__list), "Count of column names must be equal to count of data list"
                    __data.append(__list)
                return self.__executemany("INSERT INTO " + self.__table + "(" + ", ".join(self.__column_names) + ") VALUES (" + ", ".join(["?"] * len(self.__column_names)) + ")", __data)
            else:
                assert len(self.__column_names) == len(data), "Count of column names must be equal to count of data list"
                return self.__execute("INSERT INTO " + self.__table + "(" + ", ".join(self.__column_names) + ") VALUES (" + ", ".join(["?"] * len(self.__column_names)) + ")", data)
        elif isinstance(data, dict):
            __list = []
            for c in self.__column_names:
                for k, v in data.items():
                    if c == k:
                        __list.append(v)
                        break
            assert len(self.__column_names) == len(__list), "Count of column names must be equal to count of data list"
            return self.__execute("INSERT INTO " + self.__table + "(" + ", ".join(self.__column_names) + ") VALUES (" + ", ".join(["?"] * len(self.__column_names)) + ")", __list)

    def remove_old_records(self, groupping_column_names: List[str] = None) -> None:
        assert self.__connection, "No connection to database"

        if not groupping_column_names:
            groupping_column_names = self.__column_names

        self.__execute("DELETE FROM " +
                              self.__table + " WHERE rowid NOT IN (SELECT MAX(rowid) FROM " +
                              self.__table + " GROUP BY " + ", ".join(groupping_column_names) + ")")
        self.__connection.commit()
        self.__execute("VACUUM")
        self.__connection.commit()

    def read_by_cursor(self, conditions: str = None) -> sqlite3.Cursor:
        assert self.__connection, "No connection to database"

        if not conditions:
            conditions = "1 = 1"
        return self.__execute("SELECT * FROM " + self.__table + " WHERE " + conditions)

    def read_all(self, conditions: str = None, get_rowid: bool = False) -> List[Any]:
        assert self.__connection, "No connection to database"

        if not conditions:
            conditions = "1 = 1"
        return self.__execute("SELECT " + ("rowid, " if get_rowid else "") + "* FROM " + self.__table + " WHERE " + conditions).fetchall()

    def read_all_dict(self, conditions: str = None, get_rowid: bool = False) -> List[Dict[str, Any]]:
        return [{z[0]: z[1] for z in zip((["rowid"] if get_rowid else []) + self.__column_names, data)} for data in self.read_all(conditions, get_rowid)]

    def __execute(self, sql: str, *args, **kwargs) -> sqlite3.Cursor:
        if self.__wait_if_locked:
            while True:
                try:
                    ret = self.__cursor.execute(sql, *args, **kwargs)
                    break
                except sqlite3.OperationalError as e:
                    if str(e).startswith("database is locked"):
                        Log.debug("Database is locked, retrying")
                        time.sleep(Config.WAIT_FOR_BD_LOCK_S)
                    else:
                        raise e
        else:
            ret = self.__cursor.execute(sql, *args, **kwargs)

        return ret

    def __executemany(self, sql: str, *args, **kwargs) -> sqlite3.Cursor:
        if self.__wait_if_locked:
            while True:
                try:
                    ret = self.__cursor.executemany(sql, *args, **kwargs)
                    break
                except sqlite3.OperationalError as e:
                    if str(e).startswith("database is locked"):
                        Log.debug("Database is locked, retrying")
                        time.sleep(Config.WAIT_FOR_BD_LOCK_S)
                    else:
                        raise e
        else:
            ret = self.__cursor.executemany(sql, *args, **kwargs)

        return ret

    def close(self):
        try:
            self.__connection.commit()
            self.__cursor.close()
            self.__connection.close()
            self.__connection = None
        except:
            pass
