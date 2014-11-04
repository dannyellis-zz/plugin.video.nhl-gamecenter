import threading
import xbmcgui
import xbmc
from resources.lib.games_live import *
from time import sleep
from datetime import datetime

class ScoreThread(object):

    def Scoring_Updates(self):
       #while self.isRunning == True:
       #print "SHOW SCORE SETTINGS == " + ADDON.getSetting(id="score_updates")
       FIRST_TIME_THRU = 1       
       OLD_GAME_STATS = []   
       todays_date = datetime.now().strftime("%Y-%m-%d")       

       while ADDON.getSetting(id="score_updates") == 'true':        
        print "do stuff here"
        print todays_date
        json_source = getScoreBoard(todays_date)
        dialog = xbmcgui.Dialog()                        
        NEW_GAME_STATS = []
        refreshInterval = json_source['refreshInterval']
        for game in json_source['games']:                    
            gid = str(game['id'])
            ateam = game['ata']
            hteam = game['hta']
            ascore = str(game['ats'])
            hscore = str(game['hts'])
            gameclock = game['bs']                           
            NEW_GAME_STATS.append([gid,ateam,hteam,ascore,hscore,gameclock])


        if FIRST_TIME_THRU == 1:
            print "FIRST TIME"           
            FIRST_TIME_THRU = 0
        else:
            for new_item in NEW_GAME_STATS:
                #print new_item
                for old_item in OLD_GAME_STATS:                    
                    if new_item[0] == old_item[0]:
                        #print "We have a match"
                        #print new_item[0] + " == "+ old_item[0]
                        #print "is " + new_item[5] + " == " + old_item[5]
                        if new_item[3] != old_item[3] or new_item[4] != old_item[4]:
                            #or new_item[5] != old_item[5]:                           
                            if new_item[3] != old_item[3]:
                                new_item[3] = '[COLOR=FF00B7EB]'+new_item[3]+'[/COLOR]'
                            else:
                                new_item[4] = '[COLOR=FF00B7EB]'+new_item[4]+'[/COLOR]'

                            ateam = new_item[1]
                            hteam = new_item[2]
                            ascore = new_item[3]
                            hscore = new_item[4]
                            gameclock = new_item[5]
                            message = ateam + ' ' + ascore + '    ' + hteam + ' ' + hscore + '    ' + gameclock                    
                            dialog.notification('Score Update', message, ADDON_PATH+'/resources/images/nhl_logo.png', 5000, False)
                            sleep(5)

        OLD_GAME_STATS = []
        OLD_GAME_STATS = NEW_GAME_STATS
        #xbmc.sleep(int(refreshInterval)*1000)        
        sleep(int(refreshInterval))
        #print "SHOW SCORE SETTINGS == " + ADDON.getSetting(id="score_updates")
        #win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        #print str(win)
        #print "IS PLAYING VIDEO = " + str(xbmc.Player.isPlayingVideo())
