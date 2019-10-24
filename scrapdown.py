#!/usr/bin/python3

## This program is made by Clint Canada ##

import sys, requests, urllib, argparse, os, shutil
from bs4 import BeautifulSoup
from urllib.parse import urlsplit

def print_banner():
    print('███████╗ ██████╗██████╗  █████╗ ██████╗ ██████╗  ██████╗ ██╗    ██╗███╗   ██╗   ██████╗ ██╗   ██╗')        
    print('██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██║    ██║████╗  ██║   ██╔══██╗╚██╗ ██╔╝')
    print('███████╗██║     ██████╔╝███████║██████╔╝██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║   ██████╔╝ ╚████╔╝ ')
    print('╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██║  ██║██║   ██║██║███╗██║██║╚██╗██║   ██╔═══╝   ╚██╔╝  ')
    print('███████║╚██████╗██║  ██║██║  ██║██║     ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║██╗██║        ██║   ')
    print('╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝╚═╝╚═╝        ╚═╝   ')
    print()

def extract_input_fields(soup):
    fields = {}
    elements = soup.findAll('input')
    textareaelements = soup.findAll('textarea')
    selectelements = soup.findAll('select')

    for input in elements:
        type = input.get('type')

        # let us just skip inputs with no name:
        if input.get("name") == "" or input.get("name") == None:
            continue

        # for normal inputs
        if type in ('text', 'hidden', 'password', 'submit', 'image', 'tel'):
            fields[input.get('name')] = input.get('value') or ''
            continue

        # for radiobuttons and checkboxes
        if type in ('checkbox', 'radio'):
            value = ''
            if input.has_attr("checked"):
                if input.has_attr('value'):
                    value = input.get('value')
                else:
                    value = 'on'
            if 'name' in input and value:
                fields[input['name']] = value

            if not 'name' in input:
                fields[input['name']] = value

            continue

    # for textareas
    for textarea in textareaelements:
        # let us just skip textareas with no name:
        if textarea.get("name") == "" or textarea.get("name") == None:
            continue
        fields[textarea.get('name')] = textarea.string or ''

    # for select elements
    for select in selectelements:
        value = ''
        name = select.get('name')
        options = select.findAll('option')
        multiple = select.has_attr('multiple')
        selected_options = []
        first_value = ''
        last_option_value = ''

        counter = 0
        for option in options:
            if counter == 0:
                first_value = option['value']
            if option.has_attr('selected'):
                selected_options.append(option.get('value'))
            counter = counter+1

        # let us get the first option if there is no selected one
        if not selected_options and options:
            selected_options = [options[0].get('value')]
        elif not multiple and len(selected_options) == 0:
            selected_options = [first_value]
        elif not multiple and len(selected_options) > 1:
            selected_options = [selected_options[0]]
        
        fields[name] = selected_options

    return fields

def get_author():
    print('Program made by the author out of sheer laziness')
    print('to help him downloading files behind logins without browsing the site')

def main():
    print()
    print_banner()

    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to look into")
    parser.add_argument("url2", help="URL to download")
    parser.add_argument("--author",action='store_true', help="Who am I? Why I made this?")
    parser.add_argument("--mfa",action='store_true', help="mfa login")
    parser.add_argument("-o","--output", help="Output path of file downloaded")

    args = parser.parse_args()
    url = args.url
    url2 = args.url2
    mfa = args.mfa
    
    if args.author:
        get_author()
        quit()

    try:
        my_session = requests.session()
        page = my_session.get(url)
    except:
        print ("Error in getting input")
    else:
        if mfa:
            c = 3
        else:
            c = 2
        soup = BeautifulSoup(page.content, 'html.parser')

        for x in range(1,c):
            # We will get forms
            forms = soup.findAll('form')
            formcount = len(forms)

            if formcount == 0 and runsqlmap == False:
                print("URL has no detected forms")
                quit()

            if formcount == 1:
                action = str(forms[0].get('action'))
                inputs = extract_input_fields(soup)
                print("form action: "+str(forms[0].get('action')))
                formname = forms[0].get('name') or ''
                method = forms[0].get('method') or ''
            else:
                temp = input("Enter form [1 - " + str(formcount) + "]: ")
                temp = int(temp)
                if (temp < 1) or (temp > (formcount)):
                    print("Form is out of range.")
                    quit()
                inputs = extract_input_fields(forms[int(temp)-1])
                action = str(forms[int(temp)-1].get('action'))
                print("form action: "+action)
                formname = forms[int(temp)-1].get('name') or ''
                method = forms[int(temp)-1].get('method') or ''

            print("form name: "+formname+" ("+method+")")
            
            print("Getting inputs from ", url, "\r\n")
            for key,value in inputs.items():
                if not value: #for empty values we place in values
                    inputs[key] = input("Enter input for "+key+": ")

            base_url = "{0.scheme}://{0.netloc}".format(urlsplit(url))
            base_url = base_url+action

            response = my_session.post(base_url, data=inputs)
            if x==1:
                print("Going to mfa verification")
                soup = BeautifulSoup(response.content, 'html.parser')
                del inputs
            else:
                print("Posting then downloading from "+url2)
        
        # Deleting response
        del response
        response = my_session.get(url2, stream=True)
        page = response

        # Get output filename
        if args.output:
            file = args.output
        else:
            file = 'download'

        print("Saving as "+file)
        local_file = open(file, 'wb')

        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, local_file)
        del response


## start of main program ##
main()
