import logging


logger = logging.getLogger(__name__)


class UpdaterStates:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UpdaterStates, cls).__new__(cls)
            cls._instance.people_updating = False
            cls._instance.location_updating = False
            cls._instance.participation_updating = False
            cls._instance.arrival_updating = False
            cls._instance.badge_updating = False
            cls._instance.all_updating = False
        return cls._instance

    @classmethod
    def set_people_updater(cls, status: bool):
        if isinstance(status, bool):
            cls._instance.people_updating = status
        else:
            logger.warning("status must be bool!")

    @classmethod
    def set_location_updater(cls, status: bool):
        if isinstance(status, bool):
            cls._instance.location_updating = status
        else:
            logger.warning("status must be bool!")

    @classmethod
    def set_participation_updater(cls, status: bool):
        if isinstance(status, bool):
            cls._instance.participation_updating = status
        else:
            logger.warning("status must be bool!")

    @classmethod
    def set_arrival_updater(cls, status: bool):
        if isinstance(status, bool):
            cls._instance.arrival_updating = status
        else:
            logger.warning("status must be bool!")

    @classmethod
    def set_badge_updater(cls, status: bool):
        if isinstance(status, bool):
            cls._instance.badge_updating = status
        else:
            logger.warning("status must be bool!")

    @classmethod
    def start_all_updater(cls):
        cls._instance.all_updating = True

    @classmethod
    def stop_all_updater(cls):
        cls._instance.all_updating = False
