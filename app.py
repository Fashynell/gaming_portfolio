#the following flask modules are needed to send and receive info between python and html
from flask import Flask, render_template, request, redirect, url_for, session
import os
import data

app = Flask(__name__)
app.secret_key = "secret"

game_list = data.load("games.json")
platform_list = ["Browser", "Gamecube", "Mobile", "PC", "SNES", "Switch", "Wii"]
group_sort_list = ["Title", "Playtime", "Completion", "Platform", "DLC", "Rating"]

#load the normal version of the website
@app.route("/", methods=["GET", "POST"])
def games():
    #If endpoint is not triggered by a page reload
    if request.method == "POST":
        #Grabs platform into sent from the platform buttons
        platform = request.form.get("platform")
        #Update platform
        if platform:
            selected_platforms = session.get("selected_platforms", ["Browser", "Gamecube", "Mobile", "PC", "SNES", "Switch", "Wii"])
            if platform in selected_platforms:
                selected_platforms.remove(platform)
            else:
                selected_platforms.append(platform)
            session["selected_platforms"] = selected_platforms

        #Grabs group_by and sort_by info sent from the group and sort buttons
        group_by = request.form.get("group_by")
        sort_by = request.form.get("sort_by")
        #Update group_by
        if group_by != None:
            if group_by:
                if session.get("selected_group") == group_by:
                    session["selected_group"] = None
                else:
                    session["selected_group"] = group_by
        #Update sort_by
        if sort_by:
            session["selected_sort"] = sort_by
        
        #Grabs group_order and sort_order info sent from ascending and descending buttons
        group_order = request.form.get("group_order")
        sort_order = request.form.get("sort_order")
        #Update group_order and sort_order
        if group_order:
            session["selected_group_order"] = group_order
        if sort_order:
            session["selected_sort_order"] = sort_order

        #Grabs the search info sent from the search bar
        search = request.form.get("search")
        if "erase_search" in request.form or request.form["search"] == "":
            session["selected_search"] = ""
        elif search:
            session["selected_search"] = search

        return redirect(url_for("games"))

    #Receive session values upon reload
    selected_platforms = session.get("selected_platforms", ["Browser", "Gamecube", "Mobile", "PC", "SNES", "Switch", "Wii"])
    group_by = session.get("selected_group")
    sort_by = session.get("selected_sort", "Title")
    group_order = session.get("selected_group_order", "asc")
    sort_order = session.get("selected_sort_order", "asc")
    search = session.get("selected_search", "")
    
    #Re-grabs game_list and sends to database for sorting calculations
    game_list = data.load("games.json")
    completed_list = data.game_search(game_list, selected_platforms, group_by, sort_by, group_order, sort_order, search)
    
    return render_template("games.html", completed_list = completed_list, platform_list = platform_list, 
                           selected_platforms = selected_platforms, group_sort_list = group_sort_list, group_by = group_by, 
                           sort_by = sort_by, group_order = group_order, sort_order = sort_order, search = search)

#Loads a version of the website where the filters are reset
@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("games"))

@app.route("/test500")
def test_500():
    # Force a runtime error to trigger a 500
    raise Exception("Intentional test error!")

#Loads an error page if a link couldn't be found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error_id = "404 Error", error_text = "The page you requested does not exist"), 404

#Loads an error page if a server error occurs
@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", error_id = "500 Error", error_text = "An internal server error occured"), 500

#Start the wevsite from a terminal
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host = "0.0.0.0", port = port)
