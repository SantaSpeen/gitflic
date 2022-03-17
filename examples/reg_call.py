from gitflic import Gitflic, GitflicAuth

# Your authentication token.
# See: https://gitflic.ru/settings/oauth/token/create
token = "token_here"

# Creating authorized session with our token.
gf_session = GitflicAuth(token)
gf = Gitflic(gf_session)


def main():

    print("Simple call:")
    # Call method "https://api.gitflic.ru/user/me"
    call = gf.call("/user/me")
    print("gf.call:", call)

    print("\nSimple register call:")
    # Register call
    gf.user_simple = gf.reg_call("/user")

    # Request "https://api.gitflic.ru/user/me"
    reg_user_simple = gf.user_simple(end="/me")
    print("reg_user_simple:", reg_user_simple)
    print("Is reg_user_simple equals call:", reg_user_simple == call)

    print("\nAnother register call:")
    # Another way to register
    # Add at v0.11
    gf.user = gf.reg_call("/user/{user}")  # Supports "/user/{}" and "/user/%(user)s" and "/user/%s"

    # Request "https://api.gitflic.ru/user/me"
    reg_user = gf.user(user="me")
    print("reg_user:", reg_user)
    print("Is reg_user equals call:", reg_user == call)

    # Request "https://api.gitflic.ru/user/a4189db1-3e4f-4c2e-8adf-19c58c28e61f"
    author = gf.user(user="a4189db1-3e4f-4c2e-8adf-19c58c28e61f")
    print("\nAuthor: ", author)


if __name__ == '__main__':
    main()
