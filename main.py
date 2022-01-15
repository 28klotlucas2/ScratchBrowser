from flask import Flask, render_template, abort, request, redirect, session
import time
import re
import urllib.request
import json
import logging
import os
import requests

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
app = Flask("scratchbrowser")
maintinance = False
app.config["SECRET_KEY"] = os.environ["secretpassword"]


@app.before_request
def Xtra():
    if "fcb272c6-079c-4ce5-aa9c-7db84e71071b.id.repl.co" in request.url:
        return redirect("https://scratchbrowser.28klotlucas.repl.co/")
    session.permanent = True

    if maintinance and request.args.get(
            "bypass") != os.environ["secretpassword"]:
        return abort(503)


def extract_hashtags(text):
    # the regular expression
    regex = "#(\w+)"

    # extracting the hashtags
    hashtag_list = re.findall(regex, text)

    return hashtag_list


def sendreq(url):
    return urllib.request.urlopen(url).read()


def followernum(user):
    followers = int(
        re.search(
            r'Followers \(([0-9]+)\)',
            requests.get(
                f'https://scratch.mit.edu/users/{user}/followers').text,
            re.I).group(1))
    return f'{followers} on [scratch](https://scratch.mit.edu/users/{user}/followers)'


@app.route('/favicon.ico')
def favicon():
    return redirect("/static/favicon.ico")


@app.route('/')
def index():
    return render_template("home.html")


@app.route("/projects/search/")
def search():
    if request.args.get("q"):
        if request.args.get("page"):
            results = json.loads(
                sendreq("https://api.scratch.mit.edu/search/projects?q=" +
                        request.args.get("q").replace(" ", "%20") +
                        "&offset=" +
                        str((int(request.args.get("page")) - 1) * 18)))
        else:
            return redirect(request.url + "&page=1")
    else:
        return render_template("searchpage.html")
    results2 = []
    num = 0

    for i in results:
        num = num + 1
        if not num > 18:
            results2.append(i)

    if num == 0:
        return redirect("/projects/search?page=" +
                        str(int(request.args.get("page")) - 1) + "&q=" +
                        request.args.get("q"))

    return render_template("searchd.html",
                           results=results2,
                           page=int(request.args.get("page")),
                           search=True,
                           q=request.args.get("q"))


@app.route("/projects/<projid>/remixes/")
def remixes(projid):
    if not request.args.get("page"):
        results = json.loads(
            sendreq("https://api.scratch.mit.edu/projects/" + str(projid) +
                    "/remixes/"))
    else:
        results = json.loads(
            sendreq("https://api.scratch.mit.edu/projects/" + str(projid) +
                    "/remixes?offset=" +
                    str((int(request.args.get("page")) - 1) * 18)))
    results2 = []
    num = 0
    for i in results:
        num = num + 1
        if not num > 18:
            results2.append(i)

    if num == 0:
        return redirect("/projects/" + projid + "/remixes?page=" +
                        str(int(request.args.get("page")) - 1))

    return render_template("searchd.html",
                           results=results2,
                           search=False,
                           page=int(request.args.get("page")),
                           projid=projid)


@app.route("/followers/<name>/")
def followers(name):
    try:
        sendreq("https://api.scratch.mit.edu/users/" + name + "/followers/")
    except urllib.error.HTTPError:
        return "The user couldn't be found."

    followers = json.loads(
        sendreq("https://api.scratch.mit.edu/users/" + name + "/followers/"))
    projects = []

    for i in followers:
        projects.append(i["username"])

    return "<br>".join(projects)


@app.route("/search/")
def searchredirect():
    return redirect("/projects/search/")


@app.route("/projects/")
def projects():

    featured = json.loads(
        sendreq("https://api.scratch.mit.edu/proxy/featured"))
    mostremixed = []
    num = -1

    for i in featured["community_most_remixed_projects"]:
        num = num + 1
        mostremixed.append({})
        mostremixed[num]["thumbnail"] = i["thumbnail_url"]
        mostremixed[num]["title"] = i["title"]
        mostremixed[num]["creator"] = i["creator"]
        mostremixed[num]["id"] = str(i["id"])

    mostloved = []
    num = -1

    for i in featured["community_most_loved_projects"]:
        num = num + 1
        mostloved.append({})
        mostloved[num]["creator"] = i["creator"]
        mostloved[num]["thumbnail"] = i["thumbnail_url"]
        mostloved[num]["title"] = i["title"]
        mostloved[num]["id"] = str(i["id"])

    recent = json.loads(
        sendreq("https://api.scratch.mit.edu/explore/projects?mode=recent"))
    recent2 = []
    num = -1

    for i in recent:
        num = num + 1
        recent2.append({})
        recent2[num]["creator"] = i["author"]["username"]
        recent2[num]["thumbnail"] = i["images"]["200x200"]
        recent2[num]["title"] = i["title"]
        recent2[num]["id"] = str(i["id"])

    games = json.loads(
        sendreq(
            "https://api.scratch.mit.edu/explore/projects?mode=trending&q=games"
        ))
    games2 = []
    num = -1

    for i in games:
        num = num + 1
        games2.append({})
        games2[num]["creator"] = i["author"]["username"]
        games2[num]["thumbnail"] = i["images"]["200x200"]
        games2[num]["title"] = i["title"]
        games2[num]["id"] = str(i["id"])

    myprojects = json.loads(
        sendreq("https://api.scratch.mit.edu/users/28klotlucas2/projects/"))
    shamelessplug1 = []
    num = -1

    for i in myprojects:
        num = num + 1
        shamelessplug1.append({})
        shamelessplug1[num]["thumbnail"] = i["images"]["200x200"]
        shamelessplug1[num]["title"] = i["title"]
        shamelessplug1[num]["id"] = str(i["id"])

    myprojects = json.loads(
        sendreq("https://api.scratch.mit.edu/users/DarthZombot345/projects/"))
    shamelessplug2 = []
    num = -1

    for i in myprojects:
        num = num + 1
        shamelessplug2.append({})
        shamelessplug2[num]["thumbnail"] = i["images"]["200x200"]
        shamelessplug2[num]["title"] = i["title"]
        shamelessplug2[num]["id"] = str(i["id"])

    return render_template("projectlist.html",
                           mostremixed=mostremixed,
                           mostloved=mostloved,
                           shamelessplug1=shamelessplug1,
                           shamelessplug2=shamelessplug2,
                           recent=recent2,
                           games=games2)


@app.route("/projects/<projid>/spritesheet/")
def assets(projid):
    response = json.loads(
        sendreq("https://projects.scratch.mit.edu/" + projid + "/"))
    assets = []

    for i in response["targets"]:
        costname = i["name"]
        for i in i["costumes"]:
            i["name"] = costname + ": " + i["name"]
            assets.append(i)
    return render_template("assets.html", assets=assets)


@app.route("/projects/<projid>/")
def project(projid):
    response = json.loads(
        sendreq("https://api.scratch.mit.edu/projects/" + projid + "/"))

    engine = 3.0

    try:
        sendreq("https://projects.scratch.mit.edu/" + projid + "/")
    except:
        engine = 2.0

    stats = {}
    stats["views"] = str(response["stats"]["views"])
    stats["loves"] = str(response["stats"]["loves"])
    stats["favorites"] = str(response["stats"]["favorites"])
    stats["remixes"] = str(response["stats"]["remixes"])
    stats["score"] = round(
        ((((int(stats["loves"]) + int(stats["favorites"])) / 2) /
          int(stats["views"])) * 100) * 17.5, 2)

    if stats["score"] > 100:
        stats["score"] = "100"
    else:
        stats["score"] = str(stats["score"])

    response["tags"] = []

    for i in extract_hashtags(response["title"]):
        if not i in response["tags"]:
            response["tags"].append(i)

    for i in extract_hashtags(response["description"]):
        if not i in response["tags"]:
            response["tags"].append(i)

    for i in extract_hashtags(response["instructions"]):
        if not i in response["tags"]:
            response["tags"].append(i)

    if response["public"]:
        return render_template("project.html",
                               project=response,
                               stats=stats,
                               projid=projid,
                               engine=engine)
    else:
        return "To respect the privacy of others. We will not show info about unshared projects. I don't even know how you got this message. Because scratch api won't even grab info about unshared projects. So you should get an error 404 message. Scratch's servers or my servers are probably just broken."


@app.route("/projects/<projid>/play/")
def play(projid):
    return redirect("https://turbowarp.org/" + projid +
                    "/embed?interpolate&hqpen")


@app.route("/projects/<projid>/play/V2.0/")
def playalt(projid):
    return redirect("https://forkphorus.github.io/#" + projid)


@app.route("/google08ced3cd04c4329e.html")
def googlestuff():
    return render_template("google08ced3cd04c4329e.html")


@app.route("/projects/scratch.mit.edu/projects/<projid>/")
def bookmarklet(projid):
    return redirect("/projects/" + projid)


@app.route("/users/<username>/")
def userprofile(username):
    user = json.loads(sendreq("https://api.scratch.mit.edu/users/" + username))
    return render_template("user.html", user=user)


@app.route("/users/<username>/projects/")
def userprojects(username):
    if not request.args.get("page"):
        return redirect("/users/" + username + "/projects?page=1")
    else:
        results = json.loads(
            sendreq("https://api.scratch.mit.edu/users/" + username +
                    "/projects?offset=" +
                    str((int(request.args.get("page")) - 1) * 18)))

    results2 = []
    num = 0
    for i in results:
        num = num + 1
        if not num > 18:
            results2.append(i)

    if num == 0:
        return redirect("/users/" + username + "/projects?page=" +
                        str(int(request.args.get("page")) - 1))

    return render_template("searchd.html",
                           results=results2,
                           search=False,
                           page=int(request.args.get("page")),
                           user=username)


@app.route("/users/")
def users():
    users = json.loads(
        sendreq("https://scratchdb.lefty.one/v3/user/rank/global/followers"))
    response = []
    print(users)
    for i in users:
        print(i["username"])
    return response


@app.errorhandler(503)
def error503(e):
    return error404pg()


@app.errorhandler(404)
def error404(e):
    return error404pg()


def error404pg():
    return """<html class="js-focus-visible" data-js-focus-visible=""><head><title>404 Not Found</title>
</head><body><h1>Not Found</h1>
<p>""" + request.url.split(
        "http://scratchbrowser.28klotlucas.repl.co"
    )[1] + """ was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
</body></html>"""


@app.errorhandler(500)
def error500(e):
    return error404pg()


app.run(host='0.0.0.0', port=8080)
