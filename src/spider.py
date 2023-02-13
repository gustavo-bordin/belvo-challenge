import time
import json
import base64
from datetime import datetime

import scrapy

from extractor import Parser
import middlewares


class VoteForPandas(scrapy.Spider):
    name = "vote_for_pandas"

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'middlewares.FakePlatformMiddleware': 1},
    }

    form_page_url = "https://panda.belvo.io/?trial_key=A3F3D333452DF83D32A387F3FC3-GUBA"

    def __init__(self, **kwargs):
        # Convert command-line arguments into class variables.
        super().__init__(**kwargs)

        '''
        The vote for 4 out of 5 groups has already been predetermined. 
        The outcome for the final group will be determined by user input, 
        which will determine the fate of the pandas; whether they will live or die.
        '''
        self.groups = [
            {
                "name": "bearfoot_bearitone",
                "vote": "0"
            },
            {
                "name": "bearium_bearon",
                "vote": "0"
            },
            {
                "name": "stupandas_bamboozle",
                "vote": "1"
            },
            {
                "name": "bearing_embearass_goosebeary",
                "vote": "1"
            },
            {
                "name": "beary_pawsitively_forbearance",
                "vote": self.final_decision
            }
        ]

    def start_requests(self):
        for group in self.groups:
            self.logger.info("Sending to vote: %s", group)
            yield self.send_group_to_vote(group)

    def send_group_to_vote(self, group):
        '''
        Receives a specific voting token and start the voting steps. 
        The 'fake_platform' option will activate the middleware to generate 
        a random platform and bypass the GBC."
        '''
        meta = {
            "fake_platform": True,
            "group": group,
        }

        return scrapy.Request(self.form_page_url, meta=meta, dont_filter=True)

    def parse(self, response):
        '''
        This function will process the voting form page. 
        To proceed with the next request for the hastorni.js file, 
        we need to obtain the session. Additionally, we require the 
        'carnivore_value,' which is the value of an input contained 
        in the response.
        '''
        self.logger.info("Starting to vote: %s", response.meta["group"])

        key, value = Parser.Common.get_session_cookies(response.headers)
        carnivore_value = Parser.VotingPage.get_carnivore_value(response)

        hastorni_js_file_url = response.urljoin("/hastorni.js")

        '''
        carnivore_value - used in the next page to request the daxiongmao url
        group - needed to post the voting form
        os - needed to bypass GBC, used in the next page to request the daxiongmao url
        '''
        meta = {
            "carnivore_value": carnivore_value,
            "group": response.meta["group"],
            "os": response.meta["os"],
        }

        yield scrapy.Request(
            hastorni_js_file_url,
            cookies={key: value},
            headers=response.request.headers,
            callback=self.parse_hastorni_js_file,
            dont_filter=True,
            meta=meta,
        )

    def parse_hastorni_js_file(self, response):
        '''
        This function will receive the hastorni.js file content.

        We'll need this file to get two important things:

        1. Ursidae name: A array of int variable, each int represents a character code
                         Will be used to create the daxiongmao file url

        2. Rats hash:   will be used to post the voting form.
                        There is a letters mapping inside this response,
                        each letter is mapped to a random number. To get
                        the rats hash, we need to get all the letters of
                        the voting group name and their respective random
                        numbers in the mapping.

                        {B: 1, E: 2, L: 3, V: 4, O: 5}

                                                       B E L V O
                        So we need the base64 hash of: 1|2|3|4|5
        '''
        self.logger.info("Received hastorni.js: %s", response.meta["group"])

        ursidae_name = Parser.HastorniJsFile.get_ursidae_name(response.text)
        daxiongmao_file_url = Parser.HastorniJsFile.get_daxiongmao_file_url(
            response, ursidae_name
        )

        # Get rats base64, will be used in the next page to submit the vote
        rats_hash = Parser.HastorniJsFile.get_rats_hash(response)

        '''
        group: will be sent as formdata in the next page, to vote
        rats_hash: will be sent as formdata in the next page, to vote
        '''
        meta = {
            "group": response.meta["group"],
            "rats_hash": rats_hash
        }

        yield scrapy.Request(
            daxiongmao_file_url,
            headers=response.request.headers,
            cookies=response.request.cookies,
            callback=self.parse_daxiongmao_js_file,
            meta=meta
        )

    def parse_daxiongmao_js_file(self, response):
        '''
        This function will receive the daxiongmao.js file content.

        We'll need this file to get two important things:

        1. Rogue racoons hash: A md5 present in this file content
                               that will be used as formdata to post
                               the voting form

        2. A new session that will be used to vote
        '''

        self.logger.info("Received daxiongmao.js: %s",
                         response.meta["group"])

        rogue_racoons = Parser.DaxiongmaoJsFile.get_rogue_racoons_hash(
            response.text
        )
        key, value = Parser.Common.get_session_cookies(response.headers)

        group_name = response.meta["group"]["name"]
        group_vote = response.meta["group"]["vote"]
        rats_hash = response.meta["rats_hash"]

        form_data = {
            "rogue_racoons": rogue_racoons,
            "username": group_name,
            "survive": group_vote,
            "rats": rats_hash
        }

        voting_url = "https://panda.belvo.io/ursidaecarinove_eating_bambu_must_die"

        '''
        Here, even though it is the last step, we still need to pass the voting group
        inside meta. In case the request does not succeed, we can access the voting group
        in the errback and retry
        '''
        meta = {"group": response.meta["group"]}

        self.logger.info("Sending vote: %s", response.meta["group"])

        yield scrapy.FormRequest(
            voting_url,
            method="POST",
            formdata=form_data,
            headers=response.request.headers,
            cookies={key: value},
            callback=self.parse_voting_result,
            meta=meta,
            errback=self.handle_vote_failure
        )

    def parse_voting_result(self, response):
        '''
        Verifying if the response matches the expected outcome. 
        The response is considered valid if a message confirming 
        successful submission of the vote or the election results is received. 
        In case of receiving any other type of response, it is considered an error, 
        and an exception will be raised.
        '''

        def write_output_to_file(election_result):
            '''Writes the election result into a file with dinamic name'''
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"election-result-{timestamp}.json"

            with open(f"results/{file_name}", "w") as result:
                result.write(election_result)

        has_vote_suceeded_msg = "Thank you bea" in response.text
        has_election_result_msg = "pandas_future" in response.text
        has_valid_response = has_vote_suceeded_msg or has_election_result_msg

        if not has_valid_response:
            raise ValueError("Response page not expected: ", response.text)

        # If reached the election result
        if has_election_result_msg:
            try:
                election_result = json.loads(response.text)
                election_result_str = json.dumps(election_result)

                write_output_to_file(election_result_str)
                self.logger.info("Election result: %s", election_result)

            except json.JSONDecodeError as e:
                raise ValueError("Could not read election result: ", e)

    def handle_vote_failure(self, failure):
        group = failure.request.meta["group"]
        yield self.send_group_to_vote(group)
