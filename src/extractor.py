import re
import json
import base64


class Parser:
    '''
    This class is used to gather information from the Pandas Election Webpage.
    The extracted information is used to make requests.

    This class contains several subclasses, each of which represents a page or file from the
    Pandas Election website. These subclasses are organized in the same order that a user would
    access the pages:

    VotingPage -> HastorniJsFile -> DaxiongmaoJsFile.

    Additionally, the Common subclass contains information that needs to be extracted from more than one page,
    such as cookies. The purpose of that class is to provide a centralized and organized approach to get data."
    '''

    class VotingPage:
        def get_carnivore_value(response):
            """
            This function is used to extract the value of the carnivoreatingbambu input element
            from a given response object. This function searches the text of the response for an
            input element with an ID of "carnivoreatingbambu". The value of this input is crucial
            as it is used to create the URL for downloading the daxiongmao.js file, which contains
            important information needed to submit the voting form.

            # Arguments:
                - `response`: (scrapy.http.response.html.HtmlResponse)
                -- The scrapy response object

            # Returns:
                - `str`: representing the value of the input element with ID carnivoreatingbambu

            # Raises:
                - `ValueError`: raised if the input element is not found in the response
                - `ValueError`: raised if the 'value' attribute is missing from the input element.

            # Example:
                > carnivore_value = get_carnivore_value(response)
                > print(carnivore_value) # Output: 'Ursus arctos'

            """

            input_element = response.css("#carnivoreatingbambu input")
            if input_element is None:
                raise ValueError(
                    "Input element with id 'carnivoreatingbambu' not found in the response.")

            value = input_element.attrib.get('value')
            if value is None:
                raise ValueError(
                    "Value attribute not found in the input element.")

            return value

    class HastorniJsFile:
        def get_daxiongmao_file_url(response, ursidae_name):
            """
            This function generates a URL to request the daxiongmao.js file, 
            which holds the crucial information for voting, known as 'rogue-racoons.' 
            This is where the Global Blockchain Council is bypassed, as the URL is
            created using the data from the 'FakePlatformMiddleware,' simulating 
            access from a different computer.

            # Arguments:
                - `response`: (scrapy.http.response.html.HtmlResponse)
                    - The scrapy response object
                - `ursidae_name` (str) 
                    - Get in the `get_ursidae_name` function

            # Returns:
                - `str`: representing the value of the input element with ID carnivoreatingbambu

            # Raises:
                - `ValueError`: raised if the input element is not found in the response
                - `ValueError`: raised if the 'value' attribute is missing from the input element.

            # Example:
                > carnivore_value = get_carnivore_value(response)
                > print(carnivore_value) # Output: 'Ursus arctos'

            """

            # Create base64 hash of user-agent + ursidae_name + os
            os = response.meta["os"]
            ua = response.request.headers["user-agent"].decode('utf-8')
            ua_ursidae_os = f"{ua}{ursidae_name}{os}".encode('utf-8')
            ua_ursidae_os_b64 = base64.b64encode(ua_ursidae_os).decode('utf-8')

            # Create url with carnivore value + previous hash
            carnivore_value = response.meta["carnivore_value"]
            daxiongmao_file_endpoint = f"/daxiongmao.js?{carnivore_value}={ua_ursidae_os_b64}&key=aadfa"
            daxiongmao_file_url = response.urljoin(daxiongmao_file_endpoint)

            return daxiongmao_file_url

        def get_rats_hash(response):
            """
            This function generates the 'rats hash.' To create the hash, 
            the letters of the voting token are split into an array. 
            Each letter is then replaced with its corresponding numerical value, 
            which is obtained from the 'letters mapping' present in the hastorni.js file. 
            The result is an array of numbers, and the 'rats hash' is obtained by concatenating 
            these numbers with a pipe symbol and converting the result into base64


            # Arguments:
                - `response`: (scrapy.http.response.html.HtmlResponse)
                    - The scrapy response object

            # Returns:
                - `str`: a base64 hash

            # Example:
                > rats_hash = get_rats_hash(response)
                > print(rats_hash) # Output: 'MTAwMTJ8MTAwMDEzfDEwMDAxNHw...'

            """
            letters_map = Parser.HastorniJsFile._get_letters_map(response.text)
            group_name = response.meta["group"]["name"]

            group_name_letters = list(group_name)
            group_name_numbers = [str(letters_map[letter])
                                  for letter in group_name_letters]

            rats_content = "|".join(group_name_numbers)
            rats_content_encoded = rats_content.encode("utf-8")
            rats_b64 = base64.b64encode(rats_content_encoded).decode("utf-8")

            return rats_b64

        def get_ursidae_name(response_text):
            """
            Extract the name stored in the "ursidae" variable, inside the hastorni.js file.
            The name is represented as an array of character codes, which can change in each session.
            This function extracts the array of character codes and converts it to a string, creating
            a valid name.

            The returned value is used to generate a base64 hash, which will be sent as a query parameter
            to validate and download the daxiongmao.js file, containing the information needed to POST
            the voting form.

            # Arguments
            - `response_text`: (str)
            -- The response content from a scrapy request

            # Returns
                - `str`: representing the name found inside the ursidae array

            # Raises
                - `ValueError`: If the ursidae array of character codes is not found
                - `ValueError`: If the ursidae array is found but is not a valid JSON

            # Example
                > ursidae_name = get_ursidae_name(response)
                > print(ursidae_name) # ||bearcool||

            """

            find_char_codes_regex = "(?<=ursidae = ).*?(?=;)"
            char_codes_match = re.search(find_char_codes_regex, response_text)
            if char_codes_match is None:
                raise ValueError(
                    "Char codes for Ursidae name not found in response text.")

            # Extract the char codes string from the regex match
            char_codes_str = char_codes_match.group()

            # Load the char codes from the string as a JSON object
            try:
                char_codes = json.loads(char_codes_str)
            except json.JSONDecodeError as e:
                raise ValueError(
                    "Char codes string is not a valid JSON object.") from e

            ursidae_name = Parser.HastorniJsFile._convert_char_codes_to_str(
                char_codes
            )
            return ursidae_name

        def _convert_char_codes_to_str(char_codes):
            """
            Converts a list of char codes to a string

            # Arguments
                - `list`: A list with character codes

            # Returns
                - `str`: The corresponding string from the character code list

            # Raises
                - `ValueError`: If `char_codes` is not a valid list
                - `ValueError`: If the letter is not a valid integer

            # Example
                > value = _convert_char_codes_to_str([124, 124, 109, 97, 109, 97, 98, 101, 97, 114, 124, 124)
                > print(value) # ||mamabear||

            """
            try:
                return ''.join(chr(letter) for letter in char_codes)
            except TypeError as e:
                raise ValueError(
                    "Input is not a list of character codes.") from e

        def _get_letters_map(response_text):
            """
            Extract the letters mapping from the json file
            This map will be used to generate the rats hash, used to submit the evote

            # Arguments
                - `response_text`: (str)
                -- The response content from a scrapy request

            # Returns
                - `str`: representing the name found inside the ursidae array

            # Raises
                - `ValueError`: If the ursidae array of character codes is not found
                - `ValueError`: If the ursidae array is found but is not a valid JSON

            # Example
                > ursidae_name = get_ursidae_name(response)
                > print(ursidae_name) # ||bearcool||

            """
            find_map_regex = "(?<=kretzoi = ).*?(?=;)"
            map_match = re.search(find_map_regex, response_text)
            if map_match is None:
                raise ValueError("Map not found in the response.")

            map_str = map_match.group()

            try:
                map_ = json.loads(map_str)
            except json.JSONDecodeError as e:
                raise ValueError("Error decoding map") from e

            return map_

    class DaxiongmaoJsFile:
        def get_rogue_racoons_hash(response_text):
            """
            Extract the hash present in the daxiongmao.js file by using regex
            The returned value is used to post the voting form, as part of the formdata.

            # Args
                - `response_text`: (str)
                -- The response content from a scrapy request

            # Returns
                - `str`: The hash present in the response

            # Raises
                - `ValueError`: If the hash is not found

            # Example
                > hash_ = get_rogue_raccoons_hash(response)
                > print(hash_) # 0cc175b9c0f1b6a831c399e269772661
            """
            find_hash_regex = "(?<=oons\" value=\").*?(?=\")"
            hash_match = re.search(find_hash_regex, response_text)
            if hash_match is None:
                raise ValueError("Rogue raccoons hash not found in response.")

            hash_ = hash_match.group()
            return hash_

    class Common:
        def get_session_cookies(headers):
            """
            Extract the session cookie from the "Set-Cookie" header in the response.
            The session cookie is used for all subsequent requests to the voting form
            page until a final vote is submitted.

            # Args
                - headers (scrapy.http.headers.Headers): The response headers object

            # Returns
                - tuple: containing
                    - str: Key name of the cookie, in this case, it will always be "session"
                    - str: Value of the cookie, the cookie jar

            # Raises
                - ValueError: If the "Set-Cookie" header is not present in the response headers
                - ValueError: If the session cookie is not present in the "Set-Cookie" header

            # Example
                > session_cookie = get_session_cookie(response.headers)
                > print(session_cookie) # ('session', 'AbC3asdadAFDafs...')

            """
            set_cookie_header = headers.get('Set-Cookie')
            if set_cookie_header is None:
                raise ValueError(
                    "No 'Set-Cookie' header found in the response.")

            # Split the 'Set-Cookie' header into individual cookies
            cookies_str = set_cookie_header.decode("utf-8")
            cookies = cookies_str.split(";")

            # Find the session cookie
            session_cookie = None
            for cookie in cookies:
                if cookie.startswith('session='):
                    session_cookie = cookie
                    break

            if session_cookie is None:
                raise ValueError("Session cookie not found in Set-Cookie.")

            # Split the session cookie into its key and value
            key, value = session_cookie.split("=")
            return key, value
