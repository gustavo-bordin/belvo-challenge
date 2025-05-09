# 1. Getting Started

This section provides a step-by-step guide for setting up and running the project on your local machine.

### 1.1. Downloading dependencies.

This project utilizes the technologies of `Scrapy`, `Python`, `Docker`, and `Docker Compose`. To run the project locally, you will need to download and install Docker and Docker Compose. Docker will take care of downloading the rest of the required dependencies, ensuring a seamless setup experience.

> ⚠️ **Please note: if you choose to install Docker via Docker Desktop, Docker Compose will be automatically installed as well.** ⚠️

- [Click here](https://www.docker.com/products/docker-desktop/) to download Docker
- [Click here](https://docs.docker.com/compose/install/) to download Docker Compose

### 1.2. Cloning.

Before you can clone this project, it is necessary to have Git installed on your machine. If you do not have Git installed, you can download it from [here](https://git-scm.com/downloads).

Type to clone:

```
$ git clone git@github.com:gustavo-bordin/belvo-challenge.git
```

Type to navigate into the newly created folder

```
$ cd belvo-challenge
```

### 1.3. Installing dependencies

Upon cloning this repository, you will have access to the script files but not the necessary dependencies such as Scrapy and Python. To ensure everything is installed and ready to run, we will utilize Docker and Docker Compose to create a container with all the required components. This approach simplifies the installation process and ensures that the environment is consistent and easily reproducible.

Create the container:

```
$ docker-compose build
```

### 1.4. Running:

Now you have a container with python, scrapy and any other required dependency already set up. You just need to run it:

Run the container:

```
$ docker-compose up -d
```

Start the crawler

> You can choose if the pandas will burn or live by changing the `final_decision` argument.
- `1 - Will live` 
- `0 - Will die`

```
$ docker-compose exec vote-spider scrapy runspider src/spider.py -a final_decision=0
```

You have the flexibility to run the specified command as many times as you need. The output generated by the script will be saved in the form of JSON files, located inside the `results` folder.



# 2. Problem resolution

In this section, I have documented the steps taken to diagnose the issue and find a solution, including the amount of time spent on each step.

### 2.1. Identifying blockers (30m)

When reading the problem description, I understood that I would need to create a script that makes 5 POST requests. To start, I manually tried to submit a vote on the website.

The first vote was successful, but the second vote was blocked. This issue could have been caused by various blockers, but it was evident from the problem description that the voting system was aware of the different tastes that each representative has for operating systems (OS) and web browsers.

To find a solution, I tried submitting votes manually with different browsers. I first submitted a vote using Google Chrome and then submitted another vote using Microsoft Edge; it worked!

This led me to question whether using multiple browsers could allow me to submit all the necessary votes. I wondered if simply changing the user-agents would be enough.

However, my hypothesis was incorrect. When I tried using three different browsers, the third vote was still blocked. This was as I had anticipated, as the description stated that GBC was also taking into account the OS in addition to the user-agents. To bypass this, I would need to fake my OS as well.

### 2.2. Understanding how to mimic the browser behavior (30m)

To make my script work, I needed to replicate the behavior of a browser. To do this, I started by observing the steps required to submit a vote. I opened the developer tools in the network tab and began tracking my actions.

While attempting to submit a vote, I noticed that two pieces of information were required: rogue_racoons and rats. I initially tried to find these pieces of information in the HTML source, but I was unable to find anything easily accessible.

Upon further inspection, I discovered that rogue_racoons was present in the HTML, but it was being loaded using JavaScript. This would not work for my script, as the requests would not be forwarded as they are in Browsers. To solve this issue, I needed to dig into the JavaScript files and understand the logic behind generating the md5 hash.

After reviewing the hastorni.js file, I was unable to understand the code. However, with the help of the console, I was able to see what the script was outputting at each step. The information I found included my user agent, a random bear nickname, and my operating system. This was valuable information, as I could use it to fake my user agent and operating system to bypass the GBC.

Next, I replicated the URL and requested the file daxiongmao.js, which is where I found my rogue_racoons hash. I also discovered that the rats value was being generated within the same script. With the help of the console, I understood that rats was a representation of the letter values of the voting token. These values were mapped within the hastorni.js file.

With all the information I needed to submit a vote, I was able to start writing my Python script.

### 2.3. Writing the Python script (4h)

I decided to use Scrapy for my project because i know it, i like it, it's a powerful tool and it's commonly used within Belvo. It is also easy to manage middlewares and failures ;)

My first objective was to get the script to submit a single vote and then I planned to optimize it to submit more votes. The process was straightforward, as I had already identified most of the necessary steps. However, I still needed to spend some time figuring out how to handle the random data in the hastorni.js file.

Once I had adjusted my Scrapy script to retrieve the random data, I set out to make it submit multiple votes. This is where I encountered my first obstacle: sometimes my script would successfully submit two or three votes, but it would fail when I tried to submit more. After spending several hours trying to find a solution by switching fake OSs and UAs, testing different combinations, etc, I decided to code a random user agent (UA) and random operating system (OS) into my script.

To accomplish this, I used Scrapy middleware to intercept each request and add a random UA and OS, selected from a predefined list, to the request metadata. I added a flag, "fake_platform", in the request metadata to trigger the middleware and fake the UA/OS for the first request, with subsequent requests keeping the same settings.

However, even with these changes, my script was still not submitting votes consistently. It was then that I had an idea: what if I add a retry logic to my script? So, I wrote a basic retry function, and it worked! The votes were being submitted consistently.

Scrapy has a built-in middleware that automatically retries failed requests two times. However, when the voting step fails, simply retrying is not sufficient. In these cases, it is necessary to obtain a new session and operating system settings. To address this issue, I have written an errback function specifically for the voting step. This function restarts the voting process from the beginning.

Next, I needed to pass an argument to the spider to determine if the Pandas would burn or live. To keep things simple, I decided to code the script so that all the bears had a predetermined vote, with the last vote being determined by the argument I passed to the script.

The results of the voting process can be viewed in both the spider logs and in the generated election_result.json file. This file is created once all five votes have been cast.

### 2.4 Refactoring & Documenting (1h)

Finally, I decided to refactor my code by creating a separate class, "Parser", to extract data. This way, my crawler would only contain the navigation logic. The Parser class has several subclasses, each focused on a specific page, making it easier to identify where each method is being used
