# warp10-jupyter #

Jupyter extension that consists in the cell magic `%%warpscript` that execute WarpScript code.

### Requirements ###

Require Py4J and Jupyter.

To execute WarpScript code on a Warp 10 platform with this extension, the platform must embed the [Py4J plugin](https://gitlab.com/senx/warp10-plugin-py4j).

Note that WarpScripts would not be able to use the `FETCH`, `FIND`, nor `FINDSTATS` functions, unless the property `egress.clients.expose` of the target platform is set to true.

### Installation ###

From source:

```
pip install -e cellmagic
```

Or from PyPI:

```
pip install warp10-jupyter
```

Then, you can optionally copy the content of `macros/` into the macros folder of your Warp 10 platform.

### Tutorials ###

In the `notebooks/` folder:
* `1_WarpScript_example.ipynb` shows how to use cell magics with WarpScript code.
* `2_GTS_to_DataFrame.ipynb` shows how to make a Pandas DataFrame from WarpScript GTS.
