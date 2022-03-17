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

# Your authentication token.
# See: https://gitflic.ru/settings/oauth/token/create
token = "token_here"  

# Creating authorized session with our token.
gf_session = GitflicAuth(token)
gf = Gitflic(gf_session)


# Call method to get authorized user from API.
user_me = gf.call("/user/me")
print(user_me)
```