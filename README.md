## M3U Logo Matcher

Simple application that will match logos with TV programmes provided by you.

### NOTE!
This may **NOT** be 100% accurate.

### Based on
- urllib
- pathlib
- difflib
- [m3u8](https://github.com/globocom/m3u8)
- re
- os

### Usage
```bash
python3 <path-to-script> -u "<logos URL>" -m "<m3u URL/path>"
```

### Supported logo providers
Any that display logos as a file tree. A good example is [this provider](http://epg.ovh/logo).

"as a file tree". What does it mean?

![Alt text](image.png)

### Result
When everything is done, result is written in **result_\<m3u-file-name\>.txt** file, in m3u parent directory.

### Example usage
```bash
python3 <path-to-script> -u "http://epg.ovh/logo" -m "m3u_list.m3u"
```

### Available parameters
- -u/--url - logos source URL
- -m/--m3u - URL/absolute path to m3u
- -v/--verbose - enable verbose mode