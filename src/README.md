Can be loaded as a Jupyter extension `%load_ext warpscript`, which provides the cell magic `%%warpscript` that executes WarpScript code.

Can be imported as `import warpscript`, which provides `newStack()` and `newLocalStack()` that create a WarpScript execution environment (a stack).

To execute WarpScript code on a Warp 10 platform with this extension, the platform must embed the [Py4J plugin](https://warp10.io/content/03_Documentation/04_WarpScript/02_Tooling/03_Python) available [here](https://gitlab.com/senx/warp10-plugin-py4j). To enable `FETCH`, `FIND`, and `FINDSTATS` functions on this platform, set `egress.clients.expose=true`.

Warpscript code can also be executed locally (without a warp 10 platform) using `%%warpscript --local/-l` or `newLocalStack()`.

Additional resources:

* [Blog post](https://blog.senx.io/warpscript-in-jupyter-notebooks/) presenting this extension.
* [Slides](https://fr.slideshare.net/JeanCharlesVialatte/20190705-py-dataparismeetup) presented at a PyData meetup.
