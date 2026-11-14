# paint test

```topology
{
  "title": "Request / Response context",
  "vertical": true,
  "columns": [["C"], ["P"], ["K"]],
  "nodes": {
    "C": ["Customer", "browser", "customer", "client"],
    "P": ["API", "node", "waiter", "process"],
    "K": ["Database", "postgres", "warehouse", "database"]
  },
  "edges": [
    ["C", "P", "POST /order", false],
    ["P", "K", "SQL", false],
    ["K", "P", "rows", true],
    ["P", "C", "200 OK", true]
  ],
  "legend": { "flow": "Request", "back": "Response" }
}
```
