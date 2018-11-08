# warp10-jupyter #

Jupyter extension that contains a cell magic to execute WarpScript code.

### Requirements ###

Require py4j, jupyter, and optionally pandas and pickle.

Warp 10 platforms that receive the requests must embed the [Py4J plugin](https://gitlab.com/senx/warp10-plugin-py4j).

### Installation from source ###

```
pip install -e cellmagic
```

Then, you can optionally copy the content of `macros/` into the macro folder of the Warp 10 platforms that receive the requests.

### Tutorials ###

In the `notebooks/` folder:
* `1_WarpScript_example.ipynb` shows how to use cell magics with WarpScript code.
* `2_GTS_to_DataFrame.ipynb` shows how to make a Pandas DataFrame from WarpScript GTS.
