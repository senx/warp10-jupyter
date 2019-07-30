# warp10-jupyter #

Can be loaded as a Jupyter extension `%load_ext warpscript`, which provides the cell magic `%%warpscript` that executes WarpScript code.

Can be imported as `import warpscript`, which provides `newStack()` and `newLocalStack()` that create a WarpScript execution environment (a stack).

### Requirements ###

Require Py4J and Jupyter.

To execute WarpScript code on a Warp 10 platform with this extension, the platform must embed the [Py4J plugin](https://gitlab.com/senx/warp10-plugin-py4j). To enable `FETCH`, `FIND`, and `FINDSTATS` functions on this platform, set `egress.clients.expose=true`.

Warpscript code can also be executed locally (without a warp 10 platform) using `%%warpscript --local/-l` or `newLocalStack()`.

### Installation ###

From source:

```
pip install -e src
```

Or from PyPI:

```
pip install warp10-jupyter
```

### Tutorials ###

In the `notebooks/` folder:
* `1_WarpScript_example.ipynb` shows how to use cell magics with WarpScript code.
* `2_GTS_to_DataFrame.ipynb` shows how to make a Pandas DataFrame from WarpScript GTS.

### Additional resources ###

* [Blog post](https://blog.senx.io/warpscript-in-jupyter-notebooks/) presenting this extension.
* [Slides](https://fr.slideshare.net/JeanCharlesVialatte/20190705-py-dataparismeetup) presented at a PyData meetup.
