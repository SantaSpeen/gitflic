from gitflic import Gitflic, GitflicAuth


# client_id default is "cc2a5d8a-385a-4367-8b2b-bb2412eacb73", Simple gitflic.py app
# scope default is GitflicAuthScopes.ALL_READ
# redirect_url auto generate at 127.0.0.1:<randint(49152, 65535)>
# All OAuth data saved in project directory
gf_session = GitflicAuth(localhost_oauth=True)
gf = Gitflic(gf_session)


if __name__ == '__main__':
    print(gf.call('/user/me'))
