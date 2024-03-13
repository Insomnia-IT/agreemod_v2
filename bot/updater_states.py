class UpdaterStates:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UpdaterStates, cls).__new__(cls)
            cls._instance.people_updater = False
            cls._instance.location_updater = False
        return cls._instance

    def start_people_updater(self):
        self.people_updater = True

    def stop_people_updater(self):
        self.people_updater = False

    def start_location_updater(self):
        self.location_updater = True

    def stop_location_updater(self):
        self.location_updater = False

    def is_people_updater_running(self):
        return self.people_updater

    def is_location_updater_running(self):
        return self.location_updater
