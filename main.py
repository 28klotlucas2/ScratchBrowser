from flask import Flask, render_template, abort, request, redirect, session
import re
import urllib.request
import json
import logging
import os
import math

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
app = Flask("scratchbrowser")
maintinance = False
app.config["SECRET_KEY"] = os.environ["secretpassword"]


@app.before_request
def make_session_permanent():
    if "fcb272c6-079c-4ce5-aa9c-7db84e71071b.id.repl.co" in request.url:
        return redirect("https://scratchbrowser.28klotlucas.repl.co/")
    print(request.url)
    session.permanent = True


def extract_hashtags(text):

    # the regular expression
    regex = "#(\w+)"

    # extracting the hashtags
    hashtag_list = re.findall(regex, text)

    return hashtag_list


def sendreq(url):
    return urllib.request.urlopen(url).read()


@app.route('/')
def hello_world():
    return render_template("home.html")


@app.route("/projects/search/")
def projectsearchmenu():
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
def followercount(name):
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
def result():
    return redirect("/projects/search/")


@app.route("/projects/")
def featured():

    featured = json.loads(
        sendreq("https://api.scratch.mit.edu/proxy/featured"))
    mostremixed = []
    num = -1

    for i in featured["community_most_remixed_projects"]:
        num = num + 1
        mostremixed.append({})
        mostremixed[num]["thumbnail"] = i["thumbnail_url"]
        mostremixed[num]["title"] = i["title"]
        mostremixed[num]["id"] = str(i["id"])

    mostloved = []
    num = -1

    for i in featured["community_most_loved_projects"]:
        num = num + 1
        mostloved.append({})
        mostloved[num]["thumbnail"] = i["thumbnail_url"]
        mostloved[num]["title"] = i["title"]
        mostloved[num]["id"] = str(i["id"])
        print(i)

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
        print(i)

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
        print(i)

    return render_template("projectlist.html",
                           mostremixed=mostremixed,
                           mostloved=mostloved, shamelessplug1=shamelessplug1, shamelessplug2=shamelessplug2)


@app.route("/projects/<projid>/")
def projectinfo(projid):
    try:
        sendreq("https://api.scratch.mit.edu/projects/" + projid + "/")
    except:
        abort(404)
    response = json.loads(
        sendreq("https://api.scratch.mit.edu/projects/" + projid + "/"))

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

    print(response)
    print(stats)
    if response["public"]:
        return render_template("project.html",
                               project=response,
                               stats=stats,
                               projid=projid)
    else:
        return "To respect the privacy of others. We will not show info about unshared projects. I don't even know how you got this message. Because scratch api won't even grab info about unshared projects. So you should get an error 404 message. Scratch's servers or my servers are probably just broken."


@app.route("/projects/<projid>/play/")
def play(projid):
    return redirect("https://turbowarp.org/" + projid +
                    "/embed")


@app.before_request
def check_under_maintenance():
    if maintinance and not request.args.get("bypass") == os.environ[
            "secretpassword"]:  # Check if a "maintenance" file exists (whatever it is empty or not)
        abort(503)


@app.route("/google08ced3cd04c4329e.html")
def e():
    return render_template("google08ced3cd04c4329e.html")


@app.errorhandler(503)
def error503(e):
    return "I'm doing koder stuff wait till I dun is."


@app.errorhandler(404)
def error404(e):
    if request.url.startswith(
            "http://scratchbrowser.28klotlucas.repl.co/projects/"
    ) or request.url.startswith(
            "https://scratchbrowser.28klotlucas.repl.co/projects/"):
        return "Sorry, that project is either private or it dosen't exist."
    return """<html class="js-focus-visible" data-js-focus-visible=""><head><title>404 Not Found</title>
</head><body><h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
</body></html>"""


@app.errorhandler(500)
def error500(e):
    return """<html class="js-focus-visible" data-js-focus-visible=""><head><title>404 Not Found</title>
</head><body><h1>Not Found</h1>
<p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
</body></html>"""


app.run(host='0.0.0.0', port=8080)
