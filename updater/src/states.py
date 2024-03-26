class UpdaterStates:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UpdaterStates, cls).__new__(cls)
            cls._instance.people_updating = False
            cls._instance.location_updating = False
            cls._instance.all_updating = False
        return cls._instance

    @classmethod
    def start_people_updater(cls):
        cls._instance.people_updating = True

    @classmethod
    def stop_people_updater(cls):
        cls._instance.people_updating = False

    @classmethod
    def start_location_updater(cls):
        cls._instance.location_updating = True

    @classmethod
    def stop_location_updater(cls):
        cls._instance.location_updating = False

    @classmethod
    def start_all_updater(cls):
        cls._instance.all_updating = True

    @classmethod
    def stop_all_updater(cls):
        cls._instance.all_updating = False
