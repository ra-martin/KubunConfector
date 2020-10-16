from uuid import UUID
from json import JSONEncoder


class KubunJSONEncoder(JSONEncoder):
    def default(self, o):
        return o.toDict()


class KubunIdentifier():  # Enforces UUIDv4-Identifiers
    def __init__(self, ident: str):

        if not type(ident) is KubunIdentifier:
            self.ident = UUID(ident)
        else:
            self.ident = ident

        assert(self.ident.version == 4)

    def __hash__(self):
        return hash(self.ident)

    def __eq__(self, other):
        return self.ident == other.ident

    def __repr__(self):
        return f"<KubunIdentifier: { str(self.ident) }>"

    def __str__(self):
        return str(self.ident)

    def toDict(self):
        return str(self.ident)


def capitalizeIndividualWords(x):  # "bla bla" -> "Bla Bla"
    return ' '.join(map(lambda a: a.capitalize().strip(), x.split(' ')))


def clearNoneVals(d):  # No need for us to keep none-values in our dicts
    return {k: v for k, v in d.items() if v is not None}
