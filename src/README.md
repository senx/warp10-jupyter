Jupyter extension that consists in the cell magic `%%warpscript` that executes WarpScript code from Python.

To execute WarpScript code on a Warp 10 platform with this extension, the platform must embed the [Py4J plugin](https://gitlab.com/senx/warp10-plugin-py4j). To enable `FETCH`, `FIND`, and `FINDSTATS` functions on this platform, set `egress.clients.expose=true`.

Warpscript code can also be executed locally (without a warp 10 platform) using `--local/-l`.

Additional resources:

* [Blog post](https://blog.senx.io/warpscript-in-jupyter-notebooks/) presenting this extension.
* [Slides](https://fr.slideshare.net/JeanCharlesVialatte/20190705-py-dataparismeetup) presented at a PyData meetup.
