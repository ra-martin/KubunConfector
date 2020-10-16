from csv import DictReader
from pathlib import Path
import json
from typing import Iterable

from kubunconfector import KubunNode, Confector, Schema
from kubunconfector.misc import capitalizeIndividualWords

ANIMAL_SOURCE = Path('sourceData/zoo.csv')
ANIMALCLASSES_SOURCE = Path('sourceData/class.csv')
TARGET_DIGEST = Path('digest/animals.zip')
IMAGE_FILE = Path('sourceData/images.json')
ANIMAL_IMAGES = json.loads(IMAGE_FILE.read_text())


def digestAnimals(confector: Confector) -> Iterable[KubunNode]:
    with open(ANIMAL_SOURCE) as fo:
        animalReader = DictReader(fo)
        for row in animalReader:
            animalName = row['animal_name']
            coverImages = []

            if (animalImageURL := ANIMAL_IMAGES.get(animalName)) is not None:
                coverImages = [animalImageURL]

            nodeData = {
                '97a93039-b614-4b9d-ac49-b99f0d0b41e9': row['tail'] == 1,
                'bc1e7372-3c89-44e1-853b-6c97b24fb8a4': int(row['legs']),
                '6b7df71e-c21d-4162-8e9f-2eec39010362': int(row['class_type'])
            }

            node = KubunNode(capitalizeIndividualWords(animalName), coverImages)
            confector.addMultiplePropertiesToNode("animal", node, nodeData)

            yield node


def digestAnimalClasses(confector: Confector) -> Iterable[KubunNode]:
    with open(ANIMALCLASSES_SOURCE) as fo:
        animalReader = DictReader(fo)
        for row in animalReader:
            classNumber, className = int(row['Class_Number']), row['Class_Type']

            nodeData = {
                'd96e6334-0736-4010-bf3a-3c4bd142f41d': classNumber,
            }

            node = KubunNode(className)
            confector.addMultiplePropertiesToNode("animalclass", node, nodeData)

            yield node


if __name__ == "__main__":

    confector = Confector(TARGET_DIGEST)

    confector.registerSchema("animal", Schema.fromFile(Path("schemata/animal.json")))
    confector.registerSchema("animalclass", Schema.fromFile(Path("schemata/animalclass.json")))

    confector.checkSchemata()

    confector.addNodes("animal", digestAnimals(confector))
    confector.addNodes("animalclass", digestAnimalClasses(confector))

    confector.finalize({
        "kubun_ident": "animals",
        "default_tag": "animal",
        "attribution": {
            "name": "Kaggle.com",
            "url": "https://www.kaggle.com/uciml/zoo-animal-classification",
            "logo": "https://www.kaggle.com/static/images/site-logo.png"
        },
        "public": True
    })
