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
  "_preset": "blank"
}
```
