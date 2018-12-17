# Import dependencies for handling JSON, URL requests, HTML scraping, CSV Formatting
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas
import sys
import re


# finds the video link on a description page
def findVideo(htmlIn):
    divs = htmlIn.findAll("video", {"class": "landscape"})
    result = []
    # for each video class find the <source> and 'src'
    for div in divs:
        video = div.find("source").attrs['src']
        result.append(video)
    # return only the first/one video src
    return result


# find the risks and challenges text on a description page
def findRisks(htmlIn):
    # select the risks and challenges div <div>
    divs = htmlIn.find("div", {"class": "mb3 mb10-sm mb3 js-risks"})
    result = [""]
    # find all tags inside of main <div>
    children = divs.findChildren()
    result = processChildren(children)
    return result


# find the description text on a description page
def findDecsription(htmlIn):
    # select the main description <div>
    divs = htmlIn.find("div", {"class": "full-description js-full-description responsive-media formatted-lists"})
    result = [""]
    # find all tags inside of main <div>
    children = divs.findChildren()
    result = processChildren(children)
    return result


# takes set of child tags and returns an array containing all text elements appended together
def processChildren(children):
    result = [""]
    # for each tag process and append result
    for child in children:
        # checks valid tag type and text content
        if checkValidTags(child):
            # strip out white space and break characters
            divText = child.getText().strip().strip("\n")
            divText = divText.replace(u'\xa0', "")
            # If result is not empty append and continue
            if len(divText) > 0:
                result[0] += (divText + " ")

    return result


# check valid elements/html tags
def checkValidTags(element):
    check = True
    if element.name == 'video':
        check = False
    elif element.name == 'source':
        check = False
    elif element.name == ('source'):
        check = False
    elif element.name == ('img'):
        check = False
    elif element.name == ('time'):
        check = False
    elif element.find(text=False):
        check = False
    return check


def findUpdates(htmlIn):
    # select the main description <div>
    divs = htmlIn.find("div", {"class": "timeline"})
    result = [""]
    # find all tags inside of main <div>
    children = divs.findChildren()
    result = processChildren(children)
    return result


def findFAQ(htmlIn):
    # select the main description <div>
    divs = htmlIn.find("div", {"class": "NS_projects__faqs_section js-project-faqs"})
    result = [""]
    # find all tags inside of main <div>
    children = divs.findChildren()
    result = processChildren(children)
    return result


def scrapeData(urlClean):
    results = []

    appendages = ["/description", "/updates", "/faqs", "/community"]

    urlScraped = urlClean + appendages[0]
    html = urlopen(urlScraped)
    soup = BeautifulSoup(html, 'lxml')

    try:
        results.append([findDecsription(soup)[0]])
    except Exception as e:
        print(e)
        results.append("could not find description")
        print("could not find description")
    # description = findDecsription(soup)[0]

    try:
        result = re.sub("(Risks and challenges)*"
                        , ""
                        , findRisks(soup)[0])
        results.append([result])
    except Exception as e:
        print(e)
        results.append("could not find risks")
        print("could not find risks")
    # risks = findRisks(soup)[0]

    try:
        results.append([findVideo(soup)[0]])
    except Exception as e:
        print(e)
        results.append("could not find video")
        print("could not find video")
    # video = findVideo(soup)[0]

    # updates
    urlScraped = urlClean + appendages[1]
    html = urlopen(urlScraped)
    soup = BeautifulSoup(html, 'lxml')

    try:
        result = re.sub("(Project unsuccessful)*"
                        "(Project launched)*"
                        "(Project canceled)*"
                        , ""
                        , findUpdates(soup)[0])
        results.append([result])
    except Exception as e:
        print(e)
        results.append("could not find updates")
        print("could not find updates")

    # faqs
    urlScraped = urlClean + appendages[2]
    html = urlopen(urlScraped)
    soup = BeautifulSoup(html, 'lxml')

    try:
        result = re.sub("(Frequently Asked Questions)*"
                        "(Looks like there aren't any frequently asked questions yet. Ask the project creator directly\.)*"
                        "(Don't see the answer to your question?)*"
                        "(Ask the project creator directly. Ask a question)*"
                        "(Ask a question)*"
                        , ""
                        , findFAQ(soup)[0])
        results.append([result])
    except Exception as e:
        print(e)
        results.append("could not find faqs")
        print("could not find faqs")

    return results


def __main__(csvToRead, csvOutput):
    datafile = pandas.read_csv(csvToRead)
    totalRows = len(datafile['name'])

    # for each row in the csv scrape data and write back to csv
    for i in range(totalRows):
        url = json.loads(datafile.loc[i]["urls"])["web"]["project"]
        urlClean = re.sub("(\?ref=category)+.*$", "", url)

        # collect data from url
        results = scrapeData(urlClean)

        # write data to csv line
        datafile.loc[i, "description"] = results[0]
        datafile.loc[i, "risks"] = results[1]
        datafile.loc[i, "video"] = results[2]
        datafile.loc[i, "updates"] = results[3]
        datafile.loc[i, "faq"] = results[4]
        datafile.to_csv(csvOutput)


if __name__ == "__main__":
    __main__(sys.argv[1], sys.argv[2])
