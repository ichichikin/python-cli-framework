from system.metas import ConfigMeta


class Config(metaclass=ConfigMeta):
    # general
    APP_NAME = "Bare CLI Framework (rename me)"
    DEBUG = True
    MAX_LOG_FILE_SIZE_BYTES = 1024 * 1024 * 10
    LOG_FILE_BACKUP = 5
    SOFT_CTRL_C = False
    WAIT_FOR_BD_LOCK_S = 3 * 60
    SYNC_PORT = 7890
    SYNC_ATTEMPTS = 100
    SYNC_THROTTLING_S = .2
    FORBID_MULTIPROCESSING_OVERHEAD = False

    # caching
    CACHE_CLEAN_DELAY_DAYS = 30

    # telegram
    TELEGRAM_TOKEN = ""
    TELEGRAM_MEMORY_TIME_DAYS = 21
    ALLOW_WEB_ACCESS_TO_ETC = True
    TELEGRAM_WER_SERVER_PORT = 8443
