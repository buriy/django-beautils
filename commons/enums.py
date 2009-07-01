from static import Static

class Enum(Static):
    def _new_(self, attrs, parents):
        self.choices = []
        for name, attr in attrs.iteritems():
            self.choices.append((name, attr))
            self._add_to_class_(name, attr)