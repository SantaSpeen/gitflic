# gitflic

<p align="center">
    <a href="https://github.com/SantaSpeen/gitflic/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/SantaSpeen/gitflic?style=for-the-badge"></a>    
    <a href="https://github.com/SantaSpeen/gitflic/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/SantaSpeen/gitflic?style=for-the-badge"></a>    
    <a href="https://github.com/SantaSpeen"><img src="https://img.santaspeen.ru/github/magic.svg" alt="magic"></a>
    <br/>
    <a href="examples/reg_call.py">
        <img src="https://img.santaspeen.ru/github/gitflic/preview.png" alt="preview">
    </a>
    <br/>
</p>

### About 

[![PyPI download month](https://img.shields.io/pypi/dm/gitflic.svg)](https://pypi.python.org/pypi/gitflic/)
[![PyPI download week](https://img.shields.io/pypi/dd/gitflic.svg)](https://pypi.python.org/pypi/gitflic/)

This is wrapper of gitflic API.\
All API documentation is here: https://gitflic.ru/help/api/intro

### Installation

Install via pip:

`pip install gitflic`

### Example:

All examples in [examples](./examples) dir.

```python
from gitflic import Gitflic, GitflicAuth

token = "token_here"  # https://gitflic.ru/settings/oauth/token/create

gf_session = GitflicAuth(token)
gf = Gitflic(gf_session)

me_call = gf.call("/user/me")
print(me_call)

# Register call
gf.user = gf.reg_call("/user")

# Request "https://api.gitflic.ru/user/me"
me_with_reg = gf.user(end="/me")
print(me_with_reg)
print("Is me_with_reg equals me_call:", me_with_reg == me_call)

# Request "https://api.gitflic.ru/user/a4189db1-3e4f-4c2e-8adf-19c58c28e61f"
author = gf.user("/a4189db1-3e4f-4c2e-8adf-19c58c28e61f")
print("\nAuthor: ", author)
```