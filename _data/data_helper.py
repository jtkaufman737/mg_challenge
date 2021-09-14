import json


class DataHelper:
    def __init__(self, params=None, data_file="./_data/data.json"):
        self.data_file = data_file
        self.params = params
        self.election_data = self.load_election_data(data_file)

    def load_election_data(self, data_file) -> dict:
        """
        Processes JSON file data with minor error handling,
        TODO refine error logic
        """
        try:
            with open(data_file) as f:
                return json.load(f)
        except Exception as e:
            raise Exception("Internal Server Error - corrupted or missing data source")


    def flatten_results(self, data) -> dict:
        """
        Organizes all county information at the top level and creates state key on
        county objects
        """
        results = {}

        # O(n^2), can't see how to avoid it
        for state in data:
            for county in data[state]:
                results[f"{county}, {state}"] = data[state][county]

        return results


    def group_state_results(self, data) -> dict:
        """
        Recreates state results ONLY if that format is requested
        """
        results = {}

        for locality in data:
            state = locality.split(",")[1].strip()

            if state in results:
                results[state]["Democrats"].update(data[locality]["Democrats"])
                results[state]["Republicans"].update(data[locality]["Republicans"])
            else:
                results[state] = {
                    "Democrats": data[locality]["Democrats"],
                    "Republicans": data[locality]["Republicans"]
                }

        return results


    def process_winners(self, filtered_data) -> dict:
        """
        Distils each party field into the primary challenger who received most votes
        Added metadata field(s) for clarity

        TODO brittle, doesn't deal with third parties
        """
        results = {}

        for item in filtered_data:
            race = filtered_data[item]
            dems = race["Democrats"]
            reps = race["Republicans"]

            if item not in results:  # build base entry if none exists
                results[item] = {
                    "rep_winner": None,
                    "rep_winner_votes": 0,
                    "dem_winner": None,
                    "dem_winner_votes": 0,
                }

            high_dem = max(dems, key=lambda key: dems[key])
            high_rep = max(reps, key=lambda key: reps[key])

            if dems[high_dem] > results[item]["dem_winner_votes"]:
                results[item]["dem_winner"] = high_dem
                results[item]["dem_winner_votes"] = race["Democrats"][high_dem]

            if reps[high_rep] > results[item]["rep_winner_votes"]:
                results[item]["rep_winner"] = high_rep
                results[item]["rep_winner_votes"] = race["Republicans"][high_rep]

        return results

    def get_filtered_election_data(self) -> dict:
        """
        Core logic that formats and distils data into all winners based on
        parameters. Works off a copy of election data in case we may want to avoid mutating it
        for future added functionality
        """

        data = self.election_data.copy()
        flattened_data = self.flatten_results(data)

        if "level" in self.params:
            if self.params["level"] == "county":
                filtered_data = self.process_winners(flattened_data)
            elif self.params["level"] == "state":
                filtered_data = self.process_winners(
                    self.group_state_results(flattened_data)
                )
            else:
                return {
                    "statusCode": 400,
                    "status": "Bad Request - valid parameters are: county, state",
                }
        else:
            # form full dictionary of all state and locality primary winners
            county = self.process_winners(flattened_data)
            self.group_state_results(flattened_data)
            state = self.process_winners(self.group_state_results(flattened_data))
            filtered_data = county | state

        return filtered_data
