# MySQL kernel for IPython

![screenshot](https://raw.githubusercontent.com/wiki/mmisono/ipython_mysql_kernel/images/screenshot.png "screenshot")

This requires IPython 3, pexpect.  
This kernel interact with [MySQL Command-Line
Tool](https://dev.mysql.com/doc/refman/5.5/en/mysql.html) via
[pexpect](https://github.com/pexpect/pexpect).

## Install
* Use pip: `pip install git+https://github.com/mmisono/ipython_mysql_kernel`
* Checkout the source: `git clone
  https://github.com/mmisono/ipython_mysql_kernel` then `python setup.py` or
  make `~/.ipython/kernels/mysql/kernel.json` which contents is as follows:


```json
{
  "argv": [
    "python",
    "/path/to/ipython_mysql_kernel/kernel.py",
    "-f",
    "{connection_file}"
  ],
  "display_name": "mysql"
}
```


If you use `pip` or `python setup.py`, kernel files are created at ipython's
kernel directory.
(see [docs](https://ipython.org/ipython-doc/dev/development/kernels.html#kernelspecs)
for more detail).
Please don't forget to remove these files when uninstall this.

## MySQL Config
This kernel reads mysql config from `~/.ipython/mysql_config.json`.
Default config is as follwos:


```json
{
    "user"     : "root",
    "port"     : "3306",
    "host"     : "127.0.0.1",
    "charset"  : "utf8"
}
```
You can specify "password" if needed. The permission of this file should be set 600.

## Usage
`ipython console --kernel mysql` or `ipython notebook` then select mysql kernel.

## NOTE
* Use non-proportional fonts for better output in ipython notebook. You can set custom css via ipython profile.
  for example, create `~/.ipython/profile_default/static/custom/custom.css` as following:


```css
div .output_subarea pre { /* output font */
    font-family: Osaka-Mono, "MS Gothic", monospace;
    font-size: 12pt;
}
```

## TODO
* completion

## License
new BSD license
