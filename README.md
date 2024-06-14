# CLI Framework
Simple scalable framework for CLI-projects

# Running Your Code Within the Framework

The main code intended by the developer to be executed is placed in the `modules` directory. To create your own module, you need to create a corresponding file in the `modules` folder, which will contain a class matching the file name. For example, for the file `example.py`, the following code is required:

```python
from classes.log import Log

class Example:
    def __init__(self):
        Log.info('Hi!')
```

To run the module, execute the following command in the terminal:

```sh
$ python ./main.py example
```

# Configuration File system/config.py

The file contains the `Config` class, whose attributes are configurable parameters used in other classes of the framework.

## Main Parameters

- `DEBUG`, set to `True` by default. Affects the output of debugging information. Specifically, if set to `False`, messages sent through `logging.debug(...)` will not be displayed in the terminal, which can speed up code execution.
- `MAX_LOG_FILE_SIZE_BYTES`, set to `10,485,760` bytes (10 MB) by default. Limits the size of the log file.
- `LOG_FILE_BACKUP`, set to `5` by default. When rotating the log file, sets the depth of archived logs including the current one.

## Parameters of the `Cache` Class

- `CACHE_CLEAN_DELAY_DAYS`, set to `30` days by default. Sets the cache lifespan in the caching class.

## Parameters of the `Proxy` Class

- `CHECK_FOR_NEW_PROXIES_S`, set to `30` days by default. The interval for checking new proxies on the service fineproxy.org.
- `PROXY_LOGIN` sets the login for accessing the proxy list through the fineproxy.org service.
- `PROXY_PASSWORD` sets the password for accessing the proxy list through the fineproxy.org service.

## Parameters of the `TimeSeriesPlot` Class

- `PLOT_RESOLUTION`, set to `1000` elements by default. Limits the maximum amount of data displayed through the `add_data(...)` method by evenly excluding elements.
- `PLOT_HEIGHT`, set to `400` pixels by default. Adjusts the height of a single plot in pixels when calling the `show_in_browser(...)` method.

## Overriding Configurations from the Command Line

For more flexible configuration management, it is possible to override configurations when launching the framework from the command line.

For example, `$ python ./main.py info Config.DEBUG=False` overrides the `DEBUG` parameter without changing the corresponding value in the `Config` class file.

# Service Classes of the Framework

There are only two classes that can be imported from the `system` directory:
- `config.py`: Contains the configuration settings.
- `app.py`: Contains the main `App` class with the following methods.

## `App` class

The `App` class is the core system class responsible for initializing and running the application. It handles the setup of the environment, logging, signal handling, and other essential configurations.

### Main Methods

- `start(cls) -> None`: Starts the core behavior of the application.
  - Launches the main application logic defined in the `Core` class.

- `exit(cls, code: int) -> None`: Exits the application with the specified exit code.
  - `code: int`: The exit code to terminate the application with.

- `is_alive(cls) -> bool`: Returns whether the application is currently running.

- `is_master(cls) -> bool`: Returns whether the current process is the master process.

- `get_instance_id(cls) -> str`: Returns the instance ID of the current process.

- `get_argv(cls) -> list`: Returns the command line arguments.

- `get_app_path(cls) -> str`: Returns the absolute path to the application directory.

- `get_context(cls) -> 'SyncContext'`: Returns the application context.

Below are the service classes located in the `classes` directory that facilitate the development. They can be used anywhere.

## `Log` Class

The `Log` class provides a unified logging mechanism with support for console and file logging, colorized output, and configurable log levels. It leverages the Python `logging` module and is integrated with the application's configuration settings. Additionally, the configuration file sets the parameters for log file rotation, and log files will be saved to the `log` directory. Each application launch is provided with a unique ID that will be saved along with each log line, making it easy to trace application behavior even in multithreading mode.

### Main Methods

- `setup_logger(cls, root: bool = False, instance_id: str = "") -> logging.Logger`: Configures and sets up the logger.
  - `root: bool`: If `True`, sets up the root logger. Default is `False`.
  - `instance_id: str`: An identifier for the logger instance. Default is an empty string.
  - Returns the configured logger.

- `warning(cls, msg, *args, **kwargs) -> Optional[str]`: Logs a warning message.
  - `msg`: The warning message.
  - Additional arguments and keyword arguments are passed to the logger.
  - Returns the log message if `return_only` is specified in `kwargs`.

- `info(cls, msg, *args, **kwargs) -> Optional[str]`: Logs an info message.
  - `msg`: The info message.
  - Additional arguments and keyword arguments are passed to the logger.
  - Returns the log message if `return_only` is specified in `kwargs`.

- `error(cls, msg, *args, **kwargs) -> Optional[str]`: Logs an error message.
  - `msg`: The error message.
  - Additional arguments and keyword arguments are passed to the logger.
  - Returns the log message if `return_only` is specified in `kwargs`.

- `debug(cls, msg, *args, **kwargs) -> Optional[str]`: Logs a debug message.
  - `msg`: The debug message.
  - Additional arguments and keyword arguments are passed to the logger.
  - Returns the log message if `return_only` is specified in `kwargs`.

- `exception(cls, msg, *args, **kwargs) -> Optional[str]`: Logs an exception message.
  - `msg`: The exception message.
  - Additional arguments and keyword arguments are passed to the logger.
  - Returns the log message if `return_only` is specified in `kwargs`.

- `get_logger(cls) -> logging.Logger`: Retrieves the logger instance.
  - Returns the main logger instance.

## `Utils` Class

The `Utils` class provides utility methods for handling application parameters, settings, and file paths. It interacts with the application context to manage configuration settings efficiently.

### Main Methods

- `get_param(param: str, save_case: bool = False) -> Optional[str]`: Retrieves a parameter from the command line arguments.
  - `param: str`: The name of the parameter to retrieve.
  - `save_case: bool`: If `True`, preserves the case of the parameter value. Default is `False`.
  - Returns the parameter value as a string, or `None` if the parameter is not found.

- `get_setting(cls, param: str) -> Optional[Any]`: Retrieves a setting from the application context.
  - `param: str`: The name of the setting to retrieve.
  - Returns the setting value, or `None` if the setting is not found.

- `set_setting(cls, param: str, value: Any, seconds_to_live: int = 0) -> None`: Sets a setting in the application context.
  - `param: str`: The name of the setting to set.
  - `value: Any`: The value of the setting.
  - `seconds_to_live: int`: The time in seconds for the setting to live. Default is `0`.
  - Updates the setting in the context and saves it to the settings file.

- `get_absolute_path(cls, *argv: str) -> str`: Constructs an absolute path from the application path and additional arguments.
  - `*argv: str`: Additional path components.
  - Returns the absolute path as a string.

## `Cache` Class

The `Cache` class is responsible for managing caching operations, including storing and retrieving cached data, and cleaning up outdated cache files.

### Initialization

- On class initialization, the cache directory is checked for outdated files based on the configuration parameter `Config.CACHE_CLEAN_DELAY_DAYS`.
- Outdated cache files are removed, and a debug message is logged if any files are deleted.

### Main Methods

- `time(cls) -> float`: Returns the current time or the cached time if caching is in use.
  - Uses the `use_cache` method to determine if the cache should be used.
  - Returns the cached time if caching is enabled, otherwise returns the current time.

- `use_cache(cls) -> bool`: Checks if caching is enabled.
  - Returns `True` if caching is enabled (i.e., the cache parameter is greater than `0`), otherwise returns `False`.

- `get(cls, obj: str) -> Any`: Retrieves an object from the cache.
  - `obj: str`: The key for the cached object.
  - Generates a filename based on the MD5 hash of the key.
  - Raises an `EmptyCacheException` if the cache file does not exist.
  - Loads and returns the cached object from the file, logging a debug message.

- `set(cls, obj: str, value: object = None) -> object`: Stores an object in the cache.
  - `obj: str`: The key for the cached object.
  - `value: object`: The object to cache.
  - Generates a filename based on the MD5 hash of the key.
  - Serializes and stores the object in the cache file using `marshal`.
  - Logs a debug message indicating the cache file creation.
  - Returns the cached value.

## `Amqp` Class

The `Amqp` class is responsible for managing AMQP (Advanced Message Queuing Protocol) connections and operations. It uses the `pika` library to interact with an AMQP server.

### Initialization

- `__init__(self, endpoint: str = "localhost", queue: str = "default", length: int = 10, purge: bool = False)`: Initializes the AMQP connection.
  - `endpoint: str`: The AMQP server endpoint. Default is `"localhost"`.
  - `queue: str`: The name of the queue. Default is `"default"`.
  - `length: int`: The maximum length of the queue. Default is `10`.
  - `purge: bool`: Whether to purge the queue on initialization. Default is `False`.

### Main Methods

- `get_str(self) -> str`: Retrieves a message from the queue as a string.
  - Returns the message as a UTF-8 string if the message is in bytes, otherwise returns the message as is.

- `get_byte(self) -> bytes`: Retrieves a message from the queue as bytes.
  - Returns the message in bytes format if it exists, otherwise returns an empty byte array.

- `push(self, message: bytes) -> None`: Pushes a message to the queue.
  - `message: bytes`: The message to be added to the queue.

- `purge(self) -> None`: Purges all messages from the queue.

- `close(self)`: Closes the AMQP connection.
  - Attempts to close the connection and handles any exceptions that may occur.

## `Parallel` Class

The `Parallel` class is designed to manage parallel execution of tasks using multiprocessing. It provides both asynchronous and synchronous execution methods and handles the lifecycle of parallel processes.

### Initialization

- `__init__(self, process_limit: int = cpu_count() - 1, process_timeout: int = 0)`: Initializes the `Parallel` instance.
  - `process_limit: int`: The maximum number of parallel processes. Default is the number of CPU cores minus one.
  - `process_timeout: int`: The timeout for each process in seconds. Default is `0`.
  - Initializes a `NoDaemonProcessPool` to handle non-daemon processes.
  - Sets up a killer process to terminate child processes on main process exit.

### Main Methods

- `asynchronous_call(self, routine: Callable, args: Iterable = None, wait_until_worker_is_in_the_queue: bool = True, **kwargs) -> int`: Initiates an asynchronous call to a routine.
  - `routine: Callable`: The function to be executed.
  - `args: Iterable`: The arguments to pass to the function.
  - `wait_until_worker_is_in_the_queue: bool`: Whether to wait until a worker is available in the queue. Default is `True`.
  - Returns the process ID of the asynchronous call.

- `synchronous_call(cls, routine: Callable, args: Iterable = None, **kwargs) -> Any`: Executes a routine synchronously.
  - `routine: Callable`: The function to be executed.
  - `args: Iterable`: The arguments to pass to the function.
  - Returns the result of the function execution.

- `get_processes_in_progress(self) -> int`: Returns the number of processes currently in progress.

- `get_results(self, process_uid: int = None, timeout_s: float = None) -> Union[Any, List[Any]]`: Retrieves the results of the completed processes.
  - `process_uid: int`: The process ID to get results for. If `None`, retrieves results for all processes.
  - `timeout_s: float`: The timeout in seconds to wait for results. If `None`, waits indefinitely.
  - Returns the results of the specified process or all processes.

- `close(self)`: Closes the `Parallel` instance, terminating any running processes and cleaning up resources.

## `Caller` Class

The `Caller` class is designed to handle asynchronous and synchronous calls to command-line processes. It uses the `Parallel` class to manage multiple processes efficiently.

### Initialization

- `__init__(self, process_limit: int = cpu_count() - 1, process_timeout: int = 0)`: Initializes the Caller instance.
  - `process_limit: int`: The maximum number of parallel processes. Default is the number of CPU cores minus one.
  - `process_timeout: int`: The timeout for each process in seconds. Default is `0`.

### Main Methods

- `asynchronous_call(self, command_line: str, regexp_filter: str = "", wait_until_worker_is_in_the_queue: bool = False) -> int`: Initiates an asynchronous call to a command-line process.
  - `command_line: str`: The command line to be executed.
  - `regexp_filter: str`: A regular expression filter to apply to the output.
  - `wait_until_worker_is_in_the_queue: bool`: Whether to wait until a worker is available in the queue. Default is `False`.
  - Returns the process ID of the asynchronous call.

- `synchronous_call(cls, command_line: str, regexp_filter: str = "") -> List[str]`: Executes a command-line process synchronously.
  - `command_line: str`: The command line to be executed.
  - `regexp_filter: str`: A regular expression filter to apply to the output.
  - Returns a list of strings matching the regular expression filter or the entire output if no filter is provided.

- `get_processes_in_progress(self) -> int`: Returns the number of processes currently in progress.

- `get_results(self, pid: int = None, timeout_s: float = None) -> Union[List[str], List[List[str]]`: Retrieves the results of the completed processes.
  - `pid: int`: The process ID to get results for. If `None`, retrieves results for all processes.
  - `timeout_s: float`: The timeout in seconds to wait for results. If `None`, waits indefinitely.
  - Returns a list of strings or a list of lists of strings containing the results.

- `close(self)`: Closes the Caller instance, terminating any running processes.

## `Sqlite` Class

The `Sqlite` class is designed to handle SQLite database operations, including creating tables, inserting and querying data, and managing database connections.

### Initialization

- `__init__(self, database: str, column_types: List[str], column_names: List[str] = None, table: str = None, wait_if_locked: bool = True, timeout: int = 10)`: Initializes the `Sqlite` instance.
  - `database: str`: The name of the SQLite database file.
  - `column_types: List[str]`: A list of column types for the table.
  - `column_names: List[str]`: Optional list of column names. If not provided, default names are generated.
  - `table: str`: Optional name of the table. If not provided, a default name is generated.
  - `wait_if_locked: bool`: Whether to wait if the database is locked. Default is `True`.
  - `timeout: int`: The timeout for the SQLite connection. Default is `10` seconds.

### Main Methods

- `manual_commit(self) -> None`: Manually commits the current transaction.
  - Ensures there is an active database connection before committing.

- `drop_and_disconnect(self, table: str = None) -> None`: Drops the table and disconnects from the database.
  - `table: str`: The name of the table to drop. If `None`, the entire database is removed.
  - Commits the transaction, drops the table, and vacuums the database before closing the connection.

- `truncate(self) -> None`: Truncates the table by deleting all rows.
  - Deletes all rows from the table and vacuums the database.

- `manual_query(self, query: str) -> sqlite3.Cursor`: Executes a manual SQL query.
  - `query: str`: The SQL query to execute.
  - Returns the cursor for the executed query.

- `get_table_name(self) -> str`: Returns the name of the table.

- `get_column_names(self) -> List[str]`: Returns the list of column names.

- `write(self, data: Union[List[List[Any]], List[Any], List[Dict[str, Any]], Dict[str, Any]]) -> sqlite3.Cursor`: Writes data to the table.
  - `data: Union[List[List[Any]], List[Any], List[Dict[str, Any]], Dict[str, Any]]`: The data to write.
  - Supports various formats for data, including lists of lists, lists of dictionaries, and single dictionaries.
  - Ensures the data length matches the number of columns before insertion.

- `remove_old_records(self, groupping_column_names: List[str] = None) -> None`: Removes old records from the table.
  - `groupping_column_names: List[str]`: Optional list of columns to group by when removing old records. Defaults to all column names.
  - Deletes records not included in the most recent group and vacuums the database.

- `read_by_cursor(self, conditions: str = None) -> sqlite3.Cursor`: Reads data from the table based on conditions.
  - `conditions: str`: Optional SQL conditions for the query. Defaults to "1 = 1".
  - Returns the cursor for the executed query.

- `read_all(self, conditions: str = None, get_rowid: bool = False) -> List[Any]`: Reads all data from the table based on conditions.
  - `conditions: str`: Optional SQL conditions for the query. Defaults to "1 = 1".
  - `get_rowid: bool`: Whether to include the row ID in the results. Default is `False`.
  - Returns a list of all matching rows.

- `read_all_dict(self, conditions: str = None, get_rowid: bool = False) -> List[Dict[str, Any]]`: Reads all data from the table and returns it as a list of dictionaries.
  - `conditions: str`: Optional SQL conditions for the query. Defaults to "1 = 1".
  - `get_rowid: bool`: Whether to include the row ID in the results. Default is `False`.
  - Returns a list of dictionaries representing all matching rows.

- `close(self) -> None`: Closes the database connection.
  - Commits any pending transactions, closes the cursor and connection, and sets the connection to `None`.

## `Proxies` Class

The `Proxies` class is responsible for managing proxy updates and retrievals with **fineproxy.org**. It interacts with the proxy service to fetch and store proxies and provides methods to access the updated list.

### Main Methods

- `update() -> None`: Updates the list of proxies by fetching them from the proxy service.
  - Sends a GET request to the proxy service URL using the credentials defined in the `Config` class (`Config.PROXY_LOGIN` and `Config.PROXY_PASSWORD`).
  - Checks if the response status is `200` and if the response text matches the proxy format.
  - Writes the fetched proxies to `data/proxies.txt`.
  - Logs a debug message if unable to update proxies.

- `get(skip_update: bool = False) -> List[str]`: Retrieves the list of proxies.
  - `skip_update: bool`: If `True`, skips the update check. Default is `False`.
  - Checks if proxies need to be updated based on the last update timestamp (`proxy_update_ts`) and the configured interval (`Config.CHECK_FOR_NEW_PROXIES_S`).
  - Updates the list of proxies if necessary and logs a debug message.
  - Reads and returns the list of proxies from `data/proxies.txt`.
  - Returns an empty list if there is an error reading the file.

## `TelegramContext` Class

The `TelegramContext` class is designed to manage the context of a Telegram chat session, including storing and retrieving memory, sending messages, and handling user commands.

### Initialization

- `__init__(self, chat_id: str, command: str, users_text: str)`: Initializes the `TelegramContext` instance.
  - `chat_id: str`: The ID of the chat.
  - `command: str`: The command issued by the user.
  - `users_text: str`: The text entered by the user.

### Main Methods

- `get_memory(self, key: str) -> Any`: Retrieves a value from the chat's memory.
  - `key: str`: The key to retrieve.
  - Uses the `static_get_memory` method to get the value associated with the key for the chat ID.

- `set_memory(self, key: str, value: Optional[Any]) -> None`: Stores a value in the chat's memory.
  - `key: str`: The key to store the value under.
  - `value: Optional[Any]`: The value to store.
  - Ensures the key does not start with `##` or `%%`.

- `say(self, message: Union[str, list], route_back: bool = False, keyboard: Optional[list] = None) -> None`: Sends a message to the chat.
  - `message: Union[str, list]`: The message to send.
  - `route_back: bool`: If `True`, stores the current command to route back. Default is `False`.
  - `keyboard: Optional[list]`: An optional keyboard to include with the message.
  - Stores the message, command, and keyboard in memory.

- `get_text(self) -> str`: Returns the text entered by the user.

## Static Methods

- `static_get_memory(chat_id: str, key: str) -> Any`: Static method to retrieve a value from memory.
  - `chat_id: str`: The ID of the chat.
  - `key: str`: The key to retrieve.
  - Combines the chat ID and key to form the full key and retrieves the value using `Utils.get_setting`.

- `static_set_memory(chat_id: str, key: str, value: Optional[Any] = None) -> None`: Static method to store a value in memory.
  - `chat_id: str`: The ID of the chat.
  - `key: str`: The key to store the value under.
  - `value: Optional[Any]`: The value to store.
  - Combines the chat ID and key to form the full key and stores the value using `Utils.set_setting`.
  - The memory time is defined by `Config.TELEGRAM_MEMORY_TIME_DAYS` in seconds.

## `TimeSeriesPlot` Class

The `TimeSeriesPlot` class is a wrapper around the Plotly library. The main purpose of the class is to provide a convenient and consistent way to plot time series data. Some parameters of the class can be modified through the configuration file.

- `add_data(...)`: This method allows adding new data to the time series. Method parameters:
  - `name: str`: The name of the time series. A color for the time series line can be specified after the name separated by a space.
  - `timestamp: Decimal`: The timestamp of the point being added.
  - `value: Decimal`: The value of the point.

- `add_marker(...)`: This method adds a marker to the plot. Markers are convenient for showing the point where a specific event occurred. Method parameters:
  - `timestamp: Decimal`: The timestamp of the point being added.
  - `value: Decimal`: The value of the point.
  - `style: str = "none"`: Optional parameter, type of marker. A color for the marker can be specified after the type separated by a space.
  - `text: str = ""`: Optional parameter, marker text.

- `show_in_browser(...)`: This method displays the accumulated information on a plot through the default browser. Method parameters:
  - `*timeseriesplots: TimeSeriesPlot`: An unlimited number of arguments containing references to `TimeSeriesPlot` objects to be displayed on the screen.
