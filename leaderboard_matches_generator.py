#!/usr/bin/env python

'''
------------------------------------------------------------------------------------------------
Author: @Ryan_Draves
svr_lib author: @Isaac
Last Updated: 11 Mar 2019
Contact: Message @Ryan_Draves at https://forum.c1games.com/
Copyright: CC0 - completely open to edit, share, etc
Short Description: 
This is a markdown generator for the leaderboard matches posts, originally written by @876584635678890.
------------------------------------------------------------------------------------------------
Known Issues:
    - Selecting the most recent matches of the top algos likely yields repeat matches between algos.
'''

import svr_lib as svr
# Lazy k choose n function
import numpy as np

def get_heading(num_pages):
    return "This post contains replays of matches from all algos which are currently ranked on the first {}".format(num_pages) + ''' pages of the leaderboards.  
Matches out of the last 100, favoring more recent matches, were selected for each algo.  
Entries are formatted in the following way:  
Heading: `{name} by {user} = {elo}`  
Subheading: `~{average_turns}`  
Matches: `t={turns} {url} {loss_data}` (sorted by `randomness`, descending)  
Losses contain the name and current elo of the algo that defeated them (`loss_data`)\n\n'''

def get_summary(average_turns, pages, total_matches, pick, lowest_average, lowest_name, highest_average, highest_name, biggest_upsetter, biggest_upset, biggest_upset_rating, biggest_upsetted, biggest_upset_link):
    num_algos = 10 * len(pages)
    matches_picked = num_algos * pick
    return '''## Summary
{} matches between the {} top algos were considered (probably yielding repeats), and {} of those matches were picked at random, favoring recent matches. The average game length was {:.2f} turns.  
With an average amount of only {:.2f} turns `{}` was able to finish its games most quickly and `{}` had the longest games with an average of {:.2f} turns.  
The biggest underdog was `{}` with only `{}` elo because it beat `{}` in [this match]({}), a difference of `{}` elo!
\n'''.format(total_matches, num_algos, matches_picked, average_turns, lowest_average, lowest_name, highest_name, highest_average, biggest_upsetter, biggest_upset_rating, biggest_upsetted, biggest_upset_link, biggest_upset)

def get_about():
    return '''---\n[details='About']
Original idea by 876584635678890, [seen here](https://forum.c1games.com/t/leaderboard-matches-02-12-2018/708).  
Others are welcome to post Leaderboard Matches updates at their leisure. The source code for generating this post, using Isaac\'s [Terminal Server API Library](https://github.com/idraper/terminal_svr), can be viewed in [this fork](https://github.com/RyanDraves/terminal_svr). Pull requests are welcome; issues can be found at the top of the leaderboard_matches_generator.py file.
[/details]'''

def get_p(my_list):
    # I plugged this into Desmos until it looked pretty.
    unnormalized = [0.1 + 1/(((x/len(my_list))+1)**3) for x in range(len(my_list))]
    return [float(x)/sum(unnormalized) for x in unnormalized]

'''
You must put all of the code regarding the svr_lib module inside of "if __name__ == '__main__':"
since it uses the multiprocessing library.
'''
if __name__ == '__main__':
    # Variables to play with
    pick = 10
    leaderboard_pages = [1,2]
    # You can also play with the probability distrution function, get_p()

    # Variables not to play with
    output = open("output.md", "w")

    output.write(get_heading(len(leaderboard_pages)))

    algo_strings = []
    total_average_turns = 0
    leaderboard_ids = svr.get_leaderboard_ids(pages=leaderboard_pages)

    total_matches = 0
    lowest_average = 100
    lowest_name = ""
    highest_average = 0
    highest_name = ""
    biggest_upsetter = ""
    biggest_upsetted = ""
    biggest_upset = 0
    biggest_upset_rating = 0
    biggest_upset_link = ""

    # Generate the output for each algo
    for algo_name in leaderboard_ids:

        algo_id = leaderboard_ids[algo_name]
        header = "### [" + algo_name + "](https://bcverdict.github.io/?id=" + (str)(algo_id) + ") by "
        matches = svr.get_algos_matches(algo_id)
        total_matches += len(matches)
        # First k indices to choose from, pick n
        p = get_p(matches)
        selected_matches = np.random.choice(len(matches), pick, replace=False, p=p).tolist()
        average_turns = 0
        match_strings = []
        rating = 0

        # Generate the string associated with each match (if selected)
        for match_index in range(len(matches)):
            # Usernames & algo rating elo are buried in match info, so this is unique to the first match
            if match_index == 0:
                if matches[match_index]["winning_algo"]["id"] == algo_id:
                    # Some hotshot named their account without any characters so here we are
                    username = matches[match_index]["winning_algo"]["user"]
                    if username is None:
                        header += "Null"
                    else:
                        header += username
                    rating = matches[match_index]["winning_algo"]["rating"]
                    header += " = " + (str)(rating)
                else:
                    # Some hotshot named their account without any characters so here we are
                    username = matches[match_index]["losing_algo"]["user"]
                    if username is None:
                        header += "Null"
                    else:
                        header += username
                    rating = matches[match_index]["losing_algo"]["rating"]
                    header += " = " + (str)(rating)
            
            # We'll divide by len(matches) later
            average_turns += matches[match_index]["turns"]

            # Generate match string
            if match_index in selected_matches:
                match_string = (str)(matches[match_index]["turns"]) + " " + svr.get_match_str(matches[match_index]["id"])
                if matches[match_index]["losing_algo"]["id"] == algo_id:
                    match_string += " **" + matches[match_index]["winning_algo"]["name"] + "=" + (str)(matches[match_index]["winning_algo"]["rating"]) + "**"
                match_strings.append(match_string)

            # Check to see if it's the biggest upset
            if matches[match_index]["losing_algo"]["id"] == algo_id:
                elo_difference = matches[match_index]["losing_algo"]["rating"] - matches[match_index]["winning_algo"]["rating"]
                if elo_difference > biggest_upset:
                    biggest_upset = elo_difference
                    biggest_upset_rating = matches[match_index]["winning_algo"]["rating"]
                    biggest_upsetter = matches[match_index]["winning_algo"]["name"]
                    biggest_upsetted = algo_name
                    biggest_upset_link = svr.get_match_str(matches[match_index]["id"])

        # End each match for loop

        average_turns = average_turns / len(matches)
        # We'll divide by the number of algos considered later
        total_average_turns += average_turns
        algo_string = header + "  \n" + "{:.2f}".format(average_turns) + "  \n" + "[details='Matches']\n"
        for match_string in match_strings:
            algo_string += match_string + "  \n"
        algo_string += "[/details]\n"
        algo_strings.append([algo_string, rating])

        if average_turns < lowest_average:
            lowest_average = average_turns
            lowest_name = algo_name
        if average_turns > highest_average:
            highest_average = average_turns
            highest_name = algo_name
    # End each algo for loop

    num_algos = 10.0 * len(leaderboard_pages)
    output.write(get_summary(total_average_turns / num_algos, leaderboard_pages, total_matches, pick, lowest_average, lowest_name, highest_average, highest_name, biggest_upsetter, biggest_upset, biggest_upset_rating, biggest_upsetted, biggest_upset_link))

    # Sort the algo strings by each algo's elo rating
    algo_strings.sort(key=lambda x: x[1],reverse=True)

    output.write("[details='Algos']\n")
    for algo_string in algo_strings:
        output.write(algo_string[0])
        output.write("\n")
    output.write("[/details]\n")

    output.write(get_about())

    output.close()