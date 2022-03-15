from gitflic import Gitflic, GitflicAuth

token = "token_here"  # https://gitflic.ru/settings/oauth/token/create

gf_session = GitflicAuth(token)
gf = Gitflic(gf_session)


def main():
    me_call = gf.call("/user/me")
    print(me_call)

    # Register call
    gf.user = gf.reg_call("/user")

    # Request "https://api.gitflic.ru/user/me"
    me_with_reg = gf.user("/me")
    print(me_with_reg)
    print("Is me_with_reg equals me_call:", me_with_reg == me_call)

    # Request "https://api.gitflic.ru/user/a4189db1-3e4f-4c2e-8adf-19c58c28e61f"
    author = gf.user("/a4189db1-3e4f-4c2e-8adf-19c58c28e61f")
    print("\nAuthor: ", author)


if __name__ == '__main__':
    main()
