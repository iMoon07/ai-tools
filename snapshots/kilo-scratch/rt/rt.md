# round trip

```draw
{
  "module": "canvas",
  "title": "My canvas",
  "grid": true,
  "width": 900,
  "height": 520,
  "cable": "solid",
  "motion": "flow",
  "speed": 1,
  "nodes": {
    "n1": {
      "id": "n1",
      "x": 90,
      "y": 110,
      "w": 160,
      "h": 60,
      "shape": "box",
      "label": "Client",
      "sub": "browser",
      "color": "blue",
      "logo": "stack:github"
    },
    "n2": {
      "id": "n2",
      "x": 370,
      "y": 110,
      "w": 160,
      "h": 60,
      "shape": "box",
      "label": "API",
      "sub": "node",
      "color": "green",
      "logo": "programming:nodejs"
    },
    "n3": {
      "id": "n3",
      "x": 650,
      "y": 110,
      "w": 160,
      "h": 60,
      "shape": "box",
      "label": "DB",
      "sub": "postgres",
      "color": "purple",
      "logo": "stack:postgresql"
    },
    "n4": {
      "id": "n4",
      "x": 15,
      "y": -25,
      "w": 560,
      "h": 420,
      "shape": "module",
      "module": "topology",
      "moduleSpec": {
        "module": "topology",
        "title": "Edited in draw",
        "vertical": true,
        "columns": [
          [
            "C"
          ],
          [
            "P"
          ],
          [
            "K"
          ],
          [
            "G"
          ],
          [
            "X"
          ]
        ],
        "nodes": {
          "C": [
            "Customer",
            "Places an order",
            "customer",
            "actor"
          ],
          "P": [
            "Waiter",
            "Takes the order",
            "waiter",
            "process"
          ],
          "K": [
            "Chef",
            "Prepares the order",
            "cook",
            "process"
          ],
          "G": [
            "Pantry",
            "Stores ingredients",
            "warehouse",
            "store"
          ],
          "X": [
            "Cache",
            "ready to serve",
            "package",
            "store"
          ]
        },
        "edges": [
          [
            "C",
            "P"
          ],
          [
            "P",
            "K"
          ],
          [
            "K",
            "G"
          ],
          [
            "G",
            "K",
            "",
            true
          ],
          [
            "K",
            "P",
            "",
            true
          ],
          [
            "P",
            "C",
            "",
            true
          ],
          [
            "G",
            "X"
          ]
        ],
        "grid": false
      },
      "label": "",
      "color": "red"
    }
  },
  "edges": [
    {
      "from": "n1",
      "to": "n2"
    },
    {
      "from": "n2",
      "to": "n3"
    }
  ],
  "_preset": "blank",
  "selected": "n4",
  "selectedEdge": null,
  "selectedEdges": [],
  "selectedDrawing": null
}
```
