import json
import re
import os

def load(filename):
	if type(filename) != str:
		data = filename
	elif not os.path.exists(filename):
		return None
	else:
		with open(filename) as the_projects:
			data = json.load(the_projects)
	data = sorted(data, key=lambda d: d["title"])
	return data


def deplatform_games(game_list, selected_platforms):
	#Check for each game if they have a platform in the selected platforms
	deplatformed_games = []
	for game in game_list:
		platforms = game["platform"].split(" & ")
		if set(platforms) & set(selected_platforms):
			deplatformed_games.append(game)
	return deplatformed_games


def filter_games(game_list, search):
	#Check for each game if they match the inputted search
	filtered_games = []
	for game in game_list:
		full_game_info = ""
		for section in game:
			full_game_info += game[section] + " "
		if re.match((".*" + search.lower() + ":*"), full_game_info.lower()):
			filtered_games.append(game)
	return filtered_games
	
	
def group_games(game_list, group_by, group_order):
	#Group each game according to specified category, and group them in the right order
	grouped_list = {}
	
	#Group by nothing
	if group_by == None:
		grouped_list["All games"] = game_list
	
	#Group by title
	elif group_by == "Title":
		for game in game_list:
			initial = game["title"][0].upper()
			if initial not in grouped_list:
				grouped_list[initial] = []
			grouped_list[initial].append(game)
		grouped_list = dict(sorted(grouped_list.items()))
			
	#Group by playtime
	elif group_by == "Playtime":
		milestones = [10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000, 1000000]
		ranges = ["0-9 hours", "10-24 hours", "25-49 hours", "50-74 hours", "75-99 hours", "100-249 hours", "250-499 hours", "500-749 hours", "750-999 hours", "1000-2499 hours", "2500-4999 hours", "5000+ hours"]
		for r in ranges:
			grouped_list[r] = []
		for game in game_list:
			playtime = int(game["playtime"].split()[0])
			for i in range(0, 12):
				if playtime < milestones[i]:
					grouped_list[ranges[i]].append(game)
					break
		for r in ranges:
			if grouped_list[r] == []:
				grouped_list.pop(r)
					
	#Group by completion
	elif group_by == "Completion":
		statuses = ["N/A", "Dropped", "Unfinished", "Finished", "99%", "100%"]
		for status in statuses:
			for game in game_list:
				completion = game["completion"]
				if completion == status:
					if status not in grouped_list:
						grouped_list[status] = []
					grouped_list[status].append(game)
					
	#Group by platform
	elif group_by == "Platform":
		for game in game_list:
			platforms = game["platform"].split(" & ")
			for platform in platforms:
				if platform not in grouped_list:
					grouped_list[platform] = []
				grouped_list[platform].append(game)
		grouped_list = dict(sorted(grouped_list.items()))
	
	#Group by dlc
	elif group_by == "DLC":
		dlcs = ["N/A", "No", "Other", "Yes"]
		for d in dlcs:
			grouped_list[d] = []
		for game in game_list:
			dlc = game["dlc"]
			if dlc == "N/A":
				grouped_list["N/A"].append(game)
			elif dlc == "No":
				grouped_list["No"].append(game)
			elif dlc == "Yes":
				grouped_list["Yes"].append(game)
			else:
				if "Other" not in grouped_list:
					grouped_list["Other"] = []
				grouped_list["Other"].append(game)
		for d in dlcs:
			if grouped_list[d] == []:
				grouped_list.pop(d)	
	
	#Group by rating
	elif group_by == "Rating":
		ratings = ["0/10", "0.5/10", "1/10", "1.5/10", "2/10", "2.5/10", "3/10", "3.5/10", "4/10", "4.5/10", "5/10", "5.5/10", "6/10", "6.5/10", "7/10", "7.5/10", "8/10", "8.5/10", "9/10", "9.5/10", "10/10"]
		for r in ratings:
			grouped_list[r] = []
		for game in game_list:
			rating = game["rating"]
			if rating in ratings:
				grouped_list[rating].append(game)
		for r in ratings:
			if grouped_list[r] == []:
				grouped_list.pop(r)
		
	#Order the groups descending if specified
	if group_order == "desc":
		grouped_list = dict(reversed(grouped_list.items()))
	
	return grouped_list
	
	
def sort_games(game_list, sort_by, sort_order):
	#Sort each group according to specified category, and sort them in the right order
	sorted_list = {}
	
	#Sort by title
	if sort_by == "Title":
		sorted_list = {
			key: sorted(value, key=lambda x: x["title"])
			for key, value in game_list.items()
		}
	
	#Sort by playtime
	elif sort_by == "Playtime":
		sorted_list = {
			key: sorted(value, key=lambda x: (int(x["playtime"].split()[0]), x["title"]))
			for key, value in game_list.items()
		}
	
	#Sort by completion
	elif sort_by == "Completion":
		statuses = {"N/A": 0, "Dropped": 1, "Unfinished": 2, "Finished": 3, "99%": 4, "100%": 5}
		sorted_list = {
			key: sorted(value, key=lambda x: (statuses.get(x["completion"], 999), x["title"]))
			for key, value in game_list.items()		
		}
	
	#Sort by platform
	elif sort_by == "Platform":
		sorted_list = {
			key: sorted(value, key=lambda x: (-len(x["platform"].split(" & ")), x["platform"], x["title"]))
			for key, value in game_list.items()
		}
	
	#Sort by dlc
	elif sort_by == "DLC":
		dlcs = {"N/A": 0, "No": 1, "Yes": 3}
		sorted_list = {
			key: sorted(value, key=lambda x: (dlcs.get(x["dlc"], 2), x["title"]))
			for key, value in game_list.items()
		}
	
	#Sort by rating
	elif sort_by == "Rating":
		sorted_list = {
			key: sorted(value, key=lambda x: (float(x["rating"].split("/")[0]), x["title"]))
			for key, value in game_list.items()
		}
	
	#Order the games in each group descending if specified
	if sort_order == "desc":
		for group in sorted_list:
			sorted_list[group] = list(reversed(sorted_list[group]))
	
	return sorted_list
	

def game_search(game_list, selected_platforms, group_by, sort_by, group_order, sort_order, search):
	#Turn sort_by into "Title" if the grouping and sorting clash
	if group_by == sort_by:
		if group_by in ["Completion", "Platform", "DLC", "Rating"]:
			sort_by = "Title"

	#Deplatform the game list using the selected platforms
	deplatformed_list = deplatform_games(game_list, selected_platforms)
	
	#Filter the game list using the searchbar
	filtered_list = filter_games(deplatformed_list, search)
	
	#Group the game list using the grouping buttons
	grouped_list = group_games(filtered_list, group_by, group_order)
	
	#Sort the groups using the sorting buttons
	sorted_list = sort_games(grouped_list, sort_by, sort_order)
	
	#return finished game list
	return sorted_list

