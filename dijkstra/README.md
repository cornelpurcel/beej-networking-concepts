# Testing

Test with

```sh
diff <(uv run python dijkstra.py example1.json | sed 's/\/24//g') example1_output.txt
```
