from gitflic import Gitflic, GitflicAuth

# Your authentication token.
# See: https://gitflic.ru/settings/oauth/token/create
token = "token_here"  

# Creating authorized session with our token.
gf_session = GitflicAuth(token)
gf = Gitflic(gf_session)


def main():
    # Call method to get authorized user from API.
    user_me = gf.call("/user/me")
    print(user_me)


if __name__ == '__main__':
    main()
