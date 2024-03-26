class UpdaterStates:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UpdaterStates, cls).__new__(cls)
            cls._instance._people_updating = False
            cls._instance._location_updating = False
            cls._instance._all_updating = False
        return cls._instance

    @property
    def people_updating(self):
        return self._people_updating

    @people_updating.setter
    def people_updating(self, value):
        self._people_updating = value

    @property
    def location_updating(self):
        return self._location_updating

    @location_updating.setter
    def location_updating(self, value):
        self._location_updating = value

    @property
    def all_updating(self):
        return self._all_updating

    @all_updating.setter
    def all_updating(self, value):
        self._all_updating = value

    def start_people_updater(self):
        self.people_updating = True

    def stop_people_updater(self):
        self.people_updating = False

    def start_location_updater(self):
        self.location_updating = True

    def stop_location_updater(self):
        self.location_updating = False

    def start_all_updater(self):
        self.all_updating = True

    def stop_all_updater(self):
        self.all_updating = False

    def is_people_updater_running(self):
        return self.people_updating

    def is_location_updater_running(self):
        return self.location_updating

    def is_all_updater_running(self):
        return self.all_updating
