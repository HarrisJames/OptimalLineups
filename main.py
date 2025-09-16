import json
import requests

league_id = '1204723563085434880'
current_year = 2025
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


def get_traded_picks():
    contents = requests.get(league_url + "/traded_picks").text
    return json.loads(contents)


def ppt_to_double(ppt, ppt_d):
    combined = str(ppt) + '.' + str(ppt_d)
    return float(combined)


def get_num_playoff_teams():
    contents = requests.get(league_url).text
    return json.loads(contents)['settings']['playoff_teams']


def write_to_results_file(week, username_to_ppts, new_owner_by_original_username):
    draft_order = sorted(username_to_ppts, key=username_to_ppts.get)
    f = open("results.txt", "w")
    f.write("Projected Draft Results Through Week " + str(week) + "\n(name, current potential points):\n\n")
    counter = 1
    total = len(draft_order)
    playoff_teams = get_num_playoff_teams()
    for user in draft_order:
        start = [str(counter) + ".", user]
        f.write("{: >3} {: >16}".format(*start) + "{: >9}".format(f"{username_to_ppts[user]:.2f}"))
        if user in new_owner_by_original_username:
            f.write("  (-> " + new_owner_by_original_username[user] + ")")
        f.write("\n")
        if counter == total - playoff_teams:
            f.write("-------------------------------------------\n")
        counter += 1
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


def get_pick_trade_dict(rosters, userid_to_username, traded_picks):
    new_owner_by_original_username = {}
    for tp in traded_picks:
        orig_id = rosters[tp['roster_id']-1]['owner_id']
        new_id = rosters[tp['owner_id']-1]['owner_id']
        orig_username = userid_to_username[orig_id]
        new_username = userid_to_username[new_id]
        new_owner_by_original_username[orig_username] = new_username
    return new_owner_by_original_username


if __name__ == '__main__':
    traded_picks = get_traded_picks()
    first_round_trades_next_year = [tp for tp in traded_picks if tp['round'] == 1 and tp['season'] == str(current_year+1)]
    userid_to_username = map_users()
    rosters = get_rosters()

    week = rosters[0]['settings']['wins'] + rosters[0]['settings']['losses'] + rosters[0]['settings']['ties']

    username_to_ppts = get_ppts_by_user(rosters)
    new_owner_by_original_username = get_pick_trade_dict(rosters, userid_to_username, first_round_trades_next_year)
    write_to_results_file(week, username_to_ppts, new_owner_by_original_username)

