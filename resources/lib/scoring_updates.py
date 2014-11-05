import threading
import xbmcgui
import xbmc
from resources.lib.games_live import *
from time import sleep
from datetime import datetime

class ScoreThread(object):

    def Scoring_Updates(self):
       dialog = xbmcgui.Dialog()  
       title = "Score Notifications"
       nhl_logo = ADDON_PATH+'/resources/images/nhl_logo.png'
       dialog.notification(title, 'Starting...', nhl_logo, 5000, False)
       FIRST_TIME_THRU = 1       
       OLD_GAME_STATS = []   
       todays_date = datetime.now().strftime("%Y-%m-%d")        

       while ADDON.getSetting(id="score_updates") == 'true':                    
            json_source = getScoreBoard(todays_date)                                  
            NEW_GAME_STATS = []
            refreshInterval = json_source['refreshInterval']
            for game in json_source['games']:
                #Break out of loop if updates disabled
                if ADDON.getSetting(id="score_updates") == 'false':                                       
                    break

                gid = str(game['id'])
                ateam = game['ata']
                hteam = game['hta']
                ascore = str(game['ats'])
                hscore = str(game['hts'])
                gameclock = game['bs']                           
                NEW_GAME_STATS.append([gid,ateam,hteam,ascore,hscore,gameclock])


            if FIRST_TIME_THRU != 1: 
                for new_item in NEW_GAME_STATS:                    
                    if ADDON.getSetting(id="score_updates") == 'false':                                       
                        break
                    for old_item in OLD_GAME_STATS:                    
                        #Break out of loop if updates disabled
                        if ADDON.getSetting(id="score_updates") == 'false':                                       
                            break
                        if new_item[0] == old_item[0]:
                            #If the score for either team has changed and is greater than zero. Or if the game has ended show the final score
                            if  ((new_item[3] != old_item[3] and int(new_item[3]) != 0) or (new_item[4] != old_item[4] and int(new_item[4]) != 0)) or (new_item[5].find('FINAL') != -1 and old_item[5].find('FINAL') == -1):
                                #Game variables                                                    
                                ateam = new_item[1]
                                hteam = new_item[2]
                                ascore = new_item[3]
                                hscore = new_item[4]
                                gameclock = new_item[5]                            
                                
                                #Highlight goal(s) or the winning team
                                if new_item[5].find('FINAL') != -1:
                                    title = 'Final Score'
                                    if int(ascore) > int(hscore):
                                        message = '[COLOR=FF00B7EB]' + ateam + ' ' + ascore + '[/COLOR]    ' + hteam + ' ' + hscore + '    [COLOR=FF00B7EB]' + gameclock + '[/COLOR]'
                                    else:
                                        message = ateam + ' ' + ascore + '    [COLOR=FF00B7EB]' + hteam + ' ' + hscore + '[/COLOR]    [COLOR=FF00B7EB]' + gameclock  + '[/COLOR]'
                                else:
                                    title = 'Score Update'
                                    #Highlight if changed
                                    if new_item[3] != old_item[3]:
                                        ascore = '[COLOR=FF00B7EB]'+new_item[3]+'[/COLOR]'                                
                                    
                                    if new_item[4] != old_item[4]:                                
                                        hscore = '[COLOR=FF00B7EB]'+new_item[4]+'[/COLOR]'

                                    message = ateam + ' ' + ascore + '    ' + hteam + ' ' + hscore + '    ' + gameclock 

                                if ADDON.getSetting(id="score_updates") != 'false':                                       
                                    print message                   
                                    dialog.notification(title, message, nhl_logo, 5000, False)
                                    sleep(5)

            OLD_GAME_STATS = []
            OLD_GAME_STATS = NEW_GAME_STATS  
            FIRST_TIME_THRU = 0          
            sleep(int(refreshInterval))   
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())