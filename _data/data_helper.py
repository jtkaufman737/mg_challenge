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

    def flatten_county_results(self, data) -> dict:
        """
        Handles request for county level primary data, flattening data
        structure for later logic that determines winners. Reformats county
        name to include state for clarity
        """
        results = {}

        for state in self.election_data:
            for county in self.election_data[state]:
                results[f"{county}, {state}"] = self.election_data[state][county]

        return results

    def flatten_state_results(self, data) -> dict:
        """
        Collapses state results from distinct counties into only two child objects
        for democrat and republican contenders

        TODO brittle, would not handle third party candidates yet
        """
        results = {}

        for state in self.election_data:
            if not state in results:
                # create state entry for new state
                results[state] = {"Democrats": {}, "Republicans": {}}

            for county in self.election_data[state]:
                results[state]["Democrats"].update(
                    self.election_data[state][county]["Democrats"]
                )
                results[state]["Republicans"].update(
                    self.election_data[state][county]["Republicans"]
                )

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
        filtered_data = self.election_data.copy()

        if "level" in self.params:
            if self.params["level"] == "county":
                filtered_data = self.flatten_county_results(filtered_data)
            elif self.params["level"] == "state":
                filtered_data = self.flatten_state_results(filtered_data)
            else:
                return {
                    "statusCode": 400,
                    "status": "Bad Request - valid parameters are: county, state",
                }

            filtered_data = self.process_winners(filtered_data)
        else:
            # form full dictionary of all state and locality primary winners
            county = self.process_winners(self.flatten_county_results(filtered_data))
            state = self.process_winners(self.flatten_state_results(filtered_data))
            filtered_data = county | state

        return filtered_data
