<h2>
<p align="center"><img src="./assets/logo.png" width="auto" height="115"></p>
<p align="center">Kubun Data-Preparation Utility</p>
</h2>


<br/>

KubunConfector is a utility that aids users in preparing datasets for use with [Kubun](https://kubun.io).<br/> This tool is intended for internal use and is very much in an alpha-stage.<br/>
If you aim to have your data included in Kubun, please [E-Mail us](mailto:raphael@kubun.io?subject=Kubun%20Dataset) or join our Discord-Server:<br/><br/>

<p align="center"><a href="https://discord.com/invite/J5aNGUm"><img src="https://i.imgur.com/En8vQRC.png" width="auto" height="60"></a></p>


# Installation

```bash
pip install kubunconfector
```

KubunConfector requires Python >= 3.8 .
<br>

# Example Usage

Please check [the example folder](example) for a more in-depth example.<br>
Basic Workflow:

```python3
from pathlib import Path
from kubunconfector import Confector, KubunNode, Schema

def generateNodes(): # -> Iterable[KubunNode], generates our Nodes
    yield KubunNode("nodeA")
    yield KubunNode("nodeB")
    yield KubunNode("nodeC")

# Instantiate a new Confector
confector = Confector(Path("target_file.zip"))

# Register a schema for each tag
confector.registerSchema("mydataset", Schema.fromFile(Path("my_schema.json")))

# Check if all schemata are valid, also checks validity of links,
# configuration of each property etc.
confector.checkSchemata()

# Add nodes for each tag
confector.addNodes("mydataset", generateNodes())

# Finalize the dataset, generate archive
confector.finalize({
    "kubun_ident": "MyDataset", # Name of our Dataset
    "default_tag": "mydataset",
    "attribution": {            # Attribute your data!
        "name": "Kubun.io",
        "url": "https://kubun.io",
        "logo": "https://kubun.io/logo.svg"
    },
    "public": True
})
```
