"""
    This is redirect server for https://oauth.gitflic.ru/oauth/authorize
    Base URL: https://gitflic.santaspeen.ru/
    Author: @SantaSpeen
    License: MIT
"""
import json
import random
from string import ascii_letters, digits

from flask import Flask, request, redirect, abort

app = Flask("gitflic oauth redirect")
cache = {}


@app.route("/favicon.ico")
def fav():
    return redirect("https://gitflic.ru/static/image/favicon/android-icon-192x192.png", 301)


@app.route("/",  methods=["POST"])
def save_code():
    headers = request.headers

    if headers.get('Cdn-Loop') == "cloudflare":

        if headers['Cf-Connecting-Ip'] == "84.47.177.90":  # Gitflic server ip

            jsn = json.loads(request.get_data())
            cache[jsn['state']].update({"code": jsn['code']})
            return "ok", 200

    abort(403)


@app.route("/<user_code>",  methods=["GET"])
def redirect_to_localhost(user_code):
    headers = request.headers
    if headers.get('Cdn-Loop') == "cloudflare":
        ip = headers['Cf-Connecting-Ip']
        if cache.get(user_code) is None:
            return "Unknown code.", 404

        if cache[user_code]['ip'] != ip:
            return "Cannot access from your IP.", 403

        redirect_url = cache[user_code]['redirect'] + f"?code={cache[user_code]['code']}&state={user_code}"

        del cache[user_code]

        return redirect(redirect_url)

    abort(403)


@app.route("/getstate", methods=["GET"])
def getcode():
    headers = request.headers
    if headers.get('Cdn-Loop') == "cloudflare":
        ip = headers['Cf-Connecting-Ip']
        port = request.args.get('port') or abort(401)
        if port.isdigit() and 49152 <= int(port) <= 65535:
            state = ''.join([random.choice(ascii_letters + digits) for _ in range(random.randint(10, 17))])
            cache.update({state: {"ip": ip, "code": None, "redirect": f"http://localhost:{port}/"}})
            return {"state": state, "allow_from": ip}, 201

    abort(403)


if __name__ == '__main__':
    app.run("0.0.0.0", 18948, True)
