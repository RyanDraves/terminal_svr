#!/usr/bin/env python

'''
------------------------------------------------------------------------------------------------
Author: @Ryan_Draves
svr_lib author: @Isaac
Last Updated: 10 Mar 2019
Contact: Message @Ryan_Draves at https://forum.c1games.com/
Copyright: CC0 - completely open to edit, share, etc
Short Description: 
This is a markdown generator for the leaderboard matches posts, originally written by @876584635678890.
------------------------------------------------------------------------------------------------
Known Issues:
    - Selecting the most recent matches of the top algos likely yields repeat matches between algos.
    - The algos are not sorted by elo
'''

import svr_lib as svr
# Lazy k choose n function
import numpy as np

def get_heading(num_pages):
    return "This post contains replays of matches from all algos which are currently ranked on the first {}".format(num_pages) + ''' pages of the leader board.  
Only 10 out of the last 30 matches, randomly selected, will be listed for each algo.  
Entries are formatted in the following way:  
heading: `{name} by {user} = {elo}`  
subheading: `~{average_turns}`  
matches: `t={turns} {url} {loss_data}` (sorted by `randomness`, descending)  
losses are displayed bold and italic + they contain the name and current elo of the algo that defeated them (`loss_data`)\n\n'''

def get_summary(average_turns, pages, choose, pick, lowest_average, lowest_name, highest_average, highest_name):
    num_algos = 10 * len(pages)
    matches_considered = num_algos * choose
    matches_picked = num_algos * pick
    return '''## Summary
{} matches between the {} top algos were considered (probably yielding repeats), and {} of those matches were picked (at random). The average game length was {:.2f} turns.  
With an average amount of only {:.2f} turns `{}` was able to finish its games most quickly and `{}` had the longest games with an average of {:.2f} turns.
\n'''.format(matches_considered, num_algos, matches_picked, average_turns, lowest_average, lowest_name, highest_name, highest_average)

def get_about():
    return '''---\n[details='About']
Original idea by 876584635678890, [seen here](https://forum.c1games.com/t/leaderboard-matches-02-12-2018/708).  
The source code for generating this post, using Isaac\'s [Terminal Server API Library](https://github.com/idraper/terminal_svr), can be viewed in [this fork](https://github.com/RyanDraves/terminal_svr).  
Pull requests are welcome; issues can be found at the top of the leaderboard_matches_generator.py file.
[/details]'''

'''
You must put all of the code regarding the svr_lib module inside of "if __name__ == '__main__':"
since it uses the multiprocessing library.
'''
if __name__ == '__main__':
    # Variables to play with
    choose = 30
    pick = 10
    leaderboard_pages = [1,2]

    # Variables not to play with
    output = open("output.md", "w")

    output.write(get_heading(len(leaderboard_pages)))

    algo_strings = []
    total_average_turns = 0
    leaderboard_ids = svr.get_leaderboard_ids(pages=leaderboard_pages)

    lowest_average = 100
    lowest_name = ""
    highest_average = 0
    highest_name = ""

    # Generate the output for each algo
    for algo_name in leaderboard_ids:

        algo_id = leaderboard_ids[algo_name]
        header = "### " + algo_name + " by "
        matches = svr.get_algos_matches(algo_id)
        # First k indices to choose from, pick n
        selected_matches = np.random.choice(choose, pick, replace=False).tolist()
        average_turns = 0
        match_strings = []

        # Generate the string associated with each match (if selected)
        for match_index in range(len(matches)):
            # Usernames & algo elo are buried in match info, so this is unique to the first match
            if match_index == 0:
                if matches[match_index]["winning_algo"]["id"] == algo_id:
                    # Some hotshot named their account without any characters so here we are
                    username = matches[match_index]["winning_algo"]["user"]
                    if username is None:
                        header += "Null"
                    else:
                        header += username
                    header += " = " + (str)(matches[match_index]["winning_algo"]["rating"])
                else:
                    # Some hotshot named their account without any characters so here we are
                    username = matches[match_index]["losing_algo"]["user"]
                    if username is None:
                        header += "Null"
                    else:
                        header += username
                    header += " = " + (str)(matches[match_index]["losing_algo"]["rating"])
            
            # We'll divide by 100 later
            average_turns += matches[match_index]["turns"]

            if match_index in selected_matches:
                match_string = (str)(matches[match_index]["turns"]) + " " + svr.get_match_str(matches[match_index]["id"])
                if matches[match_index]["losing_algo"]["id"] == algo_id:
                    match_string += " **" + matches[match_index]["winning_algo"]["name"] + "=" + (str)(matches[match_index]["winning_algo"]["rating"]) + "**"
                match_strings.append(match_string)
        # End each match for loop

        average_turns = average_turns / 100.0
        # We'll divide by the number of algos considered later
        total_average_turns += average_turns
        algo_string = header + "  \n" + "{:.2f}".format(average_turns) + "  \n" + "[details='Matches']\n"
        for match_string in match_strings:
            algo_string += match_string + "  \n"
        algo_string += "[/details]\n"
        algo_strings.append(algo_string)

        if average_turns < lowest_average:
            lowest_average = average_turns
            lowest_name = algo_name
        if average_turns > highest_average:
            highest_average = average_turns
            highest_name = algo_name
    # End each algo for loop

    num_algos = 10.0 * len(leaderboard_pages)
    output.write(get_summary(total_average_turns / num_algos, leaderboard_pages, choose, pick, lowest_average, lowest_name, highest_average, highest_name))

    output.write("[details='Algos']\n")
    for algo_string in algo_strings:
        output.write(algo_string)
        output.write("\n")
    output.write("[/details]\n")

    output.write(get_about())

    output.close()