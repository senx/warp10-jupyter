from setuptools import setup

setup(name='warp10-jupyter',
      version='0.1',
      description='Jupyter extension that contains a cell magic to execute WarpScript code',
      #url='http://gitlab.com/jecv/warp10-jupyter',
      author='Jean-Charles Vialatte',
      author_email='jean-charles.vialatte@senx.io',
      license='Apache 2.0',
      packages=['warpscript_cellmagic'],
      install_requires=['py4j'],
      zip_safe=False)