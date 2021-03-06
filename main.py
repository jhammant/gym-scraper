#!/usr/bin/env python
# encoding: utf-8
'''
main -- Better Gym

main is a description

It defines classes_and_methods

@author:     Jon Hammant

@copyright:  2015 All rights reserved.

@license:    license

@contact:    jhammant@gmail.com
@deffield    updated: Updated
'''

import sys
import os

from optparse import OptionParser
from requests import session
from BeautifulSoup import BeautifulSoup
from lxml import html
import re
import pprint
import ast
from operator import eq
import texttable as tt
import time
from datetime import datetime, timedelta
import smtplib
import urllib2
import untangle
from time import sleep
import requests


__all__ = []
__version__ = 0.1
__date__ = '2015-02-25'
__updated__ = '2015-02-25'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    #program_usage = '''usage: spam two eggs''' # optional - will be autogenerated by optparse
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Copyright 2015 user_name (organization_name)                                            \
                Licensed under the Apache License 2.0\nhttp://www.apache.org/licenses/LICENSE-2.0"

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-i", "--in", dest="infile", help="set input path [default: %default]", metavar="FILE")
        parser.add_option("-o", "--out", dest="outfile", help="set output path [default: %default]", metavar="FILE")
        parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="set verbose")
        parser.add_option("-u", "--username", dest="username", help="Username to Connect with")
        parser.add_option("-p", "--password", dest="password", help="Password to use")
        parser.add_option("-d", "--dummy", dest="dummy", action="store_true", default=False, help="dummy run")
        parser.add_option("-w", "--write", dest="write", action="store_true", default=False, help="write output to file")
        parser.add_option("-f", "--free", dest="free", action="store_true", default=False, help="Return all free classes")
        parser.add_option("-n", "--next", dest="next", action="store_true", default=False, help="Return all free classes this day next week")
        parser.add_option("-e", "--emailaddress", dest="emailto", help="Email address to send results to")
        parser.add_option("-m", "--emailusername", dest="emailusername", help="Email username to Connect with")
        parser.add_option("-a", "--emailpassword", dest="emailpassword", help="Email Password to use")
        parser.add_option("-s", "--server", dest="server", action="store_true", default=False, help="Run constantly as server")
        
        
        # set defaults
        parser.set_defaults(outfile="./out.txt", infile="./out.txt")

        # process options
        (opts, args) = parser.parse_args(argv)
        '''
        if opts.verbose > 0:
            print("verbosity level = %d" % opts.verbose)
        if opts.infile:
            print("infile = %s" % opts.infile)
        if opts.outfile:
            print("outfile = %s" % opts.outfile)
        '''
        # MAIN BODY #

    
      
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2
    
    global finalOutput
    global siteoutput
    global classBookings
    global bookedClass
    bookedClass = []
    classBookings = []
    finalOutput = "Better Gym Booking\n"   
    #first we define all the things to do!
    
    def getGymData(username,password):
        payload = {
        'login.Email': username,
        'login.Password': password,
        'login.RedirectURL': ''
        }
        classes = { 'activity': [122,58,59,126,60,93,94,137,138,139,62,65,88,145,833,154,155,830,157,159,66,168,89,95,67,178,180,182,378,69,71], 'X-Requested-With': 'XMLHttpRequest' }

        with session() as c:
            c.get('https://gll.legendonlineservices.co.uk/enterprise/account/Login')
            c.post('https://gll.legendonlineservices.co.uk/enterprise/account/Login', data=payload)
            c.get('https://gll.legendonlineservices.co.uk/enterprise/BookingsCentre/Index')
            c.post('https://gll.legendonlineservices.co.uk/enterprise/bookingscentre/activitySelect', data=classes)
            c.post('https://gll.legendonlineservices.co.uk/enterprise/bookingscentre/TimeTable')
            response = c.get('https://gll.legendonlineservices.co.uk/enterprise/BookingsCentre/Timetable?KeepThis=true&')
            return response.text
     
    def writeOutput(dataToSave):
        f = open(opts.outfile, 'w')
        f.write(dataToSave)
        f.close()
        
    def readInput():
        f = open(opts.infile, 'r')
        temp = f.read()
        return temp
    
    def fixOutput(myHtml):
            soup = BeautifulSoup(myHtml)
            typeofclass = soup.findAll("div", {"class" : "activityHeader"})
            classtimes = soup.findAll("table",{ "class" : "resultTable"})
            allresults = str(soup.findAll(True,{ "class" : ["activityHeader", "resultTable"]}))
            data = allresults
            tree = html.fromstring(str(data))
            strip = " </div>, <table class=\"resultTable\" cellpadding=\"0\" cellspacing=\"0\"><tr class=\"titleRow\"><td class=\"col1\">Club</td><td class=\"col2\">Day</td><td class=\"col3\">Date</td><td class=\"col4\">Time</td><td class=\"col5\">Availability</td><td class=\"col6\">Price</td><td class=\"col7\">Instructor</td><td class=\"col8\">&nbsp;</td></tr><tr><td>"
            temp = data.replace(strip, '\n')
            classheader = "<div class=\"activityHeader\">"
            temp = temp.replace(classheader, "NEW:")
            end = "</td></tr></table>,"
            temp = temp.replace(end, "SPLIT\n")
            last = "</td></tr></table>"
            temp = temp.replace(last, "SPLIT\n")
            morerubbish = "class=\"jTip100\"><img src=\"/media/siteimages/moreInfoBlue.gif\" alt=\"Click for More info\" style=\"border:0px;"
            temp = temp.replace(morerubbish, "")
            morerubbish = "class=\"addLink\">[ Add to Basket ]</a>"
            temp = temp.replace(morerubbish, "")
            temp = temp.replace(")\n",")</td><td>")
            temp = temp.replace("</td><td>","SPLIT")
            temp = temp.replace("<td>", "")
            temp = temp.replace("<tr>", "")
            temp = temp.replace("<tr class=\"altRow\">", "")
            temp = temp.replace("<tr ", "")
            temp = temp.replace("<a href=\"GetPrice?instanceId=", "")
            temp = temp.replace("rel=\"GetPrice?instanceId=", "")
            temp = temp.replace("id=\"price", "")
            temp = temp.replace("href=\"#\" onclick=\"addBooking(", "")
            temp = temp.replace("<a id=\"slot", "")
            temp = temp.replace("\)\"", "")
            temp = temp.replace("\" \" /></a>", "")
            temp = temp.replace("\"", "")
            temp = temp.replace("\)", "")
            temp = temp.replace("\) ", "")
            temp = temp.replace("\n ", "")
            temp = temp.replace("\n", "")
            temp = temp.replace("</td><tr>","SPLIT")
            temp = temp.replace("</td></tr>","SPLIT")
            dividedbyclass = temp.split("SPLIT")
            classname = ""
            outPutList = []
            x = 0
            while len(dividedbyclass) != 0:
                templist = []
                if "NEW:" in str(dividedbyclass[0]):
                    classname = str(dividedbyclass[0]).replace("NEW:", "")
                    del(dividedbyclass[0])
                    templist.append(classname)
                else:
                    templist.append(classname)                  
                if len(dividedbyclass) != 0:
                        for y in range(0, 8):
                            try:
                                templist.append(dividedbyclass[0])
                                del(dividedbyclass[0])
                            except:
                                break
                if len(templist) == 9:
                    if templist[8] != "[ FULLY BOOKED ]":
                        templist[6] = str(templist[6]).split(" ")[0]
                        templist[8] = str(templist[8]).split(" ")[0]
                    outPutList.append(templist) 
            x = x+1  
            return outPutList
    
    def getFreeClases(inputList):
        tempList = []
        for x in range(0, len(inputList)):
            if inputList[x][8] != "[ FULLY BOOKED ]":
                tempList.append(inputList[x])
            
        if len(tempList) == 0:
            tempList.append("All Full!!!") 
        return tempList
    
    def getNextWeek(inputList):
        tempList = []
        for x in range(0, len(inputList)):
            classDay = datetime.strptime(str(inputList[x][3]), '%d/%m/%Y')
            now = datetime.now()
            if (classDay - now) > timedelta(days = 6):
                tempList.append(inputList[x])
            
        if len(tempList) == 0:
            tempList.append("All Full!!!") 
        return tempList
    
           
    if opts.dummy:
        siteoutput = readInput()
    else:
        siteoutput = getGymData(opts.username, opts.password)
        
    if opts.write:
        t = writeOutput(siteoutput)
        
        
    if len(siteoutput) < 10:
        print "Something went wrong getting data! Exiting!"
        exit
             
    siteoutput = fixOutput(siteoutput)
    
    if opts.verbose:
        tab = tt.Texttable()
        tab._max_width = 0
        for i in range(0, len(siteoutput)):
            tab.add_row(siteoutput[i])
        finalOutput = finalOutput + tab.draw()    

    def outPutNextWeek():
        nextsiteoutput = getNextWeek(siteoutput)
        tab = tt.Texttable()
        tab._max_width = 0
        global finalOutput
        global siteoutput
        for i in range(0, len(nextsiteoutput)):
            temprow = []
            temprow.append(str(nextsiteoutput[i][0]).replace(" ( Clissold )", ""))
            temprow.append(nextsiteoutput[i][2])
            temprow.append(nextsiteoutput[i][3])
            temprow.append(nextsiteoutput[i][4])
            temprow.append(nextsiteoutput[i][5])
            temprow.append(nextsiteoutput[i][7])
            temprow.append("mailto:" + opts.emailusername + '@gmail.com' + "?subject=GYMCLASS:" + str(nextsiteoutput[i][8]))
            tab.add_row(temprow)
        finalOutput = finalOutput + "******************************\n"
        finalOutput = finalOutput + "Classes on this day next week!\n"
        finalOutput = finalOutput + "******************************\n"
        finalOutput = finalOutput + tab.draw()
    
    def outPutNextFree():
        global finalOutput
        global siteoutput
        siteoutput = getFreeClases(siteoutput)
        tab = tt.Texttable()
        tab._max_width = 0
        for i in range(0, len(siteoutput)):
            temprow = []
            temprow.append(str(siteoutput[i][0]).replace(" ( Clissold )", ""))
            temprow.append(siteoutput[i][2])
            temprow.append(siteoutput[i][3])
            temprow.append(siteoutput[i][4])
            temprow.append(siteoutput[i][5])
            temprow.append(siteoutput[i][7])
            temprow.append("mailto:" + opts.emailusername + '@gmail.com' + "?subject=GYMCLASS:" + str(siteoutput[i][8]))
            
            tab.add_row(temprow)
        finalOutput = finalOutput + "\n*****************\n"
        finalOutput = finalOutput + "All Free Classes\n"
        finalOutput = finalOutput + "*****************\n"
        finalOutput = finalOutput + tab.draw()

    
    def sendEmailOut():
        global finalOutput
        fromaddr = opts.emailusername + '@gmail.com'
        toaddrs  = opts.emailto

        # Credentials (if needed)
        username = opts.emailusername
        password = opts.emailpassword

        # The actual mail send
        server = smtplib.SMTP_SSL('smtp.gmail.com:465')
        server.ehlo()
        server.login(username,password)
        msg = "\r\n".join([
              "From: " + fromaddr,
              "To: " + toaddrs,
              "Subject: Daily Gym Update",
              "",
              finalOutput
              ])
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
        
    def getEmailResponses():
        FEED_URL = 'https://mail.google.com/mail/feed/atom'
        r = requests.get('https://mail.google.com/mail/feed/atom', auth=(opts.emailusername, opts.emailpassword))
        soup = BeautifulSoup(r.text)
        titlesOfMails = soup.findAll("title")
        bookingReturn = []
        for y in range(0, len(titlesOfMails)):
            if str(titlesOfMails[y]).find("GYMCLASS") != -1:
                temp = str(titlesOfMails[y]).replace("GYMCLASS:", "")
                temp = temp.replace("<title>", "")
                temp = temp.replace("</title>", "")
                bookingReturn.append(temp)
        return bookingReturn
    
    def bookClass(classID):
        #book the class
        print "Booking class"
        print classID
        payload = {
        'login.Email': opts.username,
        'login.Password': opts.password,
        'login.RedirectURL': ''
        }
        
        classes = { 'booking': classID } 
        
        instance = { 'instanceId': classID }
        
        with session() as d:
            d.get('https://gll.legendonlineservices.co.uk/enterprise/account/Login')
            d.post('https://gll.legendonlineservices.co.uk/enterprise/account/Login', data=payload)
            d.get('https://gll.legendonlineservices.co.uk/enterprise/BookingsCentre/Index')
            d.get('https://gll.legendonlineservices.co.uk/enterprise/BookingsCentre/AddBooking', data=classes)
            d.get('https://gll.legendonlineservices.co.uk/enterprise/BookingsCentre/GetPrice', data=instance)
            d.get('https://gll.legendonlineservices.co.uk/enterprise/Basket/Pay')
            d.get('https://gll.legendonlineservices.co.uk/enterprise/basket/paymentconfirmed')
            
            
        
    
    if opts.next:
        outPutNextWeek()
        
    if opts.free:
        outPutNextFree()
    
    if opts.emailto:
        sendEmailOut()    
    
    
    if opts.server:
        print "Starting up as Gym Booking Server"
        startuptime = datetime.now()
        outPutNextWeek()
        outPutNextFree()
        sendEmailOut()
        loopCounter = 0
        while True:
            sleep(100)
            loopCounter = loopCounter + 1
            newClass = getEmailResponses()
            if newClass != "":
                myClass = newClass
            if myClass != "":
                currentHour = datetime.now().hour
                if currentHour >= 22:
                    if bookedClass != myClass:
                        bookClass(myClass[0])
                        bookedClass = myClass
                if currentHour == 4:
                    bookedClass = []
                if loopCounter >= 860:
                    #email out the new day
                    outPutNextWeek()
                    outPutNextFree()
                    sendEmailOut()
                    loopCounter = 0
                    
                        
                    
                
                       
             
        
        
    print finalOutput
    
    print getEmailResponses()
    
    
    
    
    
    
if __name__ == "__main__":
    #if DEBUG:
        #sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'main_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
        
    sys.exit(main())
