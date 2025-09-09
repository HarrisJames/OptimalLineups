import json
import requests

league_id = '1204723563085434880'
league_url = "https://api.sleeper.app/v1/league/" + league_id

def map_users():
    contents = requests.get(league_url + "/users").text
    id_to_username = {}
    for user in json.loads(contents):
        id_to_username[user['user_id']] = user['display_name']
    return id_to_username


def get_rosters():
    contents = requests.get(league_url + "/rosters").text
    return json.loads(contents)


def ppt_to_double(ppt, ppt_d):
    combined = str(ppt) + '.' + str(ppt_d)
    return float(combined)


def get_num_playoff_teams():
    contents = requests.get(league_url).text
    return json.loads(contents)['settings']['playoff_teams']


def write_to_results_file(week, username_to_ppts):
    draft_order = sorted(username_to_ppts, key=username_to_ppts.get)
    f = open("results.txt", "w")
    f.write("Projected Draft Results Through Week " + str(week) + "\n(name, current potential points):\n\n")
    counter = 1
    total = len(draft_order)
    playoff_teams = get_num_playoff_teams()
    for user in draft_order:
        f.write(str(counter) + ". " + user + " " + str(username_to_ppts[user]) + "\n")
        if counter == total - playoff_teams:
            f.write("----------------------------\n")
        counter = counter + 1
    f.close()


def get_ppts_by_user(rosters):
    username_to_ppts = {}
    for roster in rosters:
        settings = roster['settings']
        ppt = settings['ppts']
        ppt_d = settings['ppts_decimal']
        owner_id = roster['owner_id']
        if owner_id in userid_to_username:
            username = userid_to_username[owner_id]
            username_to_ppts[username] = ppt_to_double(ppt, ppt_d)
    return username_to_ppts


if __name__ == '__main__':
    userid_to_username = map_users()
    rosters = get_rosters()

    week = rosters[0]['settings']['wins'] + rosters[0]['settings']['losses'] + rosters[0]['settings']['ties']

    username_to_ppts = get_ppts_by_user(rosters)
    write_to_results_file(week, username_to_ppts)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
