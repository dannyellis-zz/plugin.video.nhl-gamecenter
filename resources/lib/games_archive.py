from xml.dom.minidom import parseString
from datetime import datetime
import time
import pickle
 
from resources.lib.common import *
 
 
def getSeasons():
    #Dowload the xml file
    xmlFile = downloadFile('http://gamecenter.nhl.com/nhlgc/servlets/allarchives',{'date' : 'true', 'isFlex' : 'true'})
   
    #Get available seasons
    xml = parseString(xmlFile)
    seasons = xml.getElementsByTagName("season")
   
    seasonList = []
   
    for season in reversed(seasons):
        print season.attributes["id"].value
        if (season.attributes["id"].value == "2007"):#Links don't work
            break
        elif (season.attributes["id"].value == "2008"):#Links don't work
            break
        elif (season.attributes["id"].value == "2009"):#Links don't work
            break
        else:
            aSeason = [int(season.attributes["id"].value)]
            dates = season.getElementsByTagName("g")
 
            for date in reversed(dates):
                if len(date.childNodes[0].nodeValue)>10: #Fix for alternative date format
                    if aSeason[-1] != int(date.childNodes[0].nodeValue[5:7]):
                        aSeason.append(int(date.childNodes[0].nodeValue[5:7]))
                else:
                    if aSeason[-1] != int(date.childNodes[0].nodeValue[:2]):
                        aSeason.append(int(date.childNodes[0].nodeValue[:2]))
           
            seasonList.append(aSeason)
 
    #Save thelist of seasons
    pickle.dump(seasonList, open(os.path.join(ADDON_PATH_PROFILE, 'archive'),"wb"))
   
    return seasonList
 
 
def getGames(url):
   
    #Split the url
    splittedURL = url.split("/")
    typeOfVideo = splittedURL[1]
    year = splittedURL[2]
    month = splittedURL[3]
 
    #Download the xml file
    if typeOfVideo == 'condensed' or int(year) >= 2012:
        values = {'season' : year, 'isFlex' : 'true', 'month' : month, 'condensed' : 'true'}
    else:
        values = {'season' : year, 'isFlex' : 'true', 'month' : month}
   
    xmlFile = downloadFile('http://gamecenter.nhl.com/nhlgc/servlets/archives',values)
    #print xmlFile
   
    #Parse the xml file
    xml = parseString(xmlFile)
    games = xml.getElementsByTagName("game")
   
    #
    gameList = []
   
    #Latest game
    latestGame = games[0].getElementsByTagName("date")[0].childNodes[0].nodeValue[:10]
    latestGame = datetime.fromtimestamp(time.mktime(time.strptime(latestGame,"%Y-%m-%d"))).strftime(xbmc.getRegion('dateshort'))
   
    #Get available games
    for game in games:
        gid = game.getElementsByTagName("gid")[0].childNodes[0].nodeValue
        date = game.getElementsByTagName("date")[0].childNodes[0].nodeValue
        homeTeam = game.getElementsByTagName("homeTeam")[0].childNodes[0].nodeValue
        awayTeam = game.getElementsByTagName("awayTeam")[0].childNodes[0].nodeValue
        streamURL = game.getElementsByTagName("publishPoint")[0].childNodes[0].nodeValue

        season = game.getElementsByTagName("season")[0].childNodes[0].nodeValue
        g_type = game.getElementsByTagName("type")[0].childNodes[0].nodeValue
        g_id = game.getElementsByTagName("id")[0].childNodes[0].nodeValue

        game_id =  season + g_type.zfill(2) + g_id.zfill(4) 
 
        awayGoals = ''
        homeGoals = ''  
        if SHOWSCORE == 'true':
            try:
                awayGoals = game.getElementsByTagName("awayGoals")[0].childNodes[0].nodeValue
                homeGoals = game.getElementsByTagName("homeGoals")[0].childNodes[0].nodeValue
                #Change color of goals
                awayGoals = '[COLOR=FF00B7EB]'+ awayGoals + '[/COLOR]'
                homeGoals = '[COLOR=FF00B7EB]'+ homeGoals + '[/COLOR]'
            except:
                pass
       
        #Versus string
        versus = 31400
        if ALTERNATIVEVS == 'true':
            versus = 31401
 
        #Localize the date
        date2 = date[:10]
        date = datetime.fromtimestamp(time.mktime(time.strptime(date2,"%Y-%m-%d"))).strftime(xbmc.getRegion('dateshort'))
       
        #Get teamnames
        teams = getTeams()
       
        #Game title
 
        if awayTeam in teams and homeTeam in teams:
            name = date + ': ' + teams[awayTeam][TEAMNAME] + " " + awayGoals + " " + LOCAL_STRING(versus) + " " + teams[homeTeam][TEAMNAME] + " " + homeGoals
        else:
            name = date + ': ' + awayTeam + " " + awayGoals + " " + LOCAL_STRING(versus) + " " + homeTeam + " " + homeGoals
       
        if typeOfVideo != "lastnight": #Show all games
            gameList.append([name, gid, homeTeam, awayTeam, streamURL, game_id])
        elif latestGame == date: #show only latest games
            gameList.append([name, gid, homeTeam, awayTeam, streamURL, game_id])
   
    #Save the list of games
    pickle.dump(gameList, open(os.path.join(ADDON_PATH_PROFILE, 'games'),"wb"))
       
    return gameList
 
 
def getGameLinks(url):
   
    #Video type
    typeOfVideo = url.split("/")[1]
    year = url.split("/")[2]
   
    if typeOfVideo == "lastnight":
        if "archive" in url:
            typeOfVideo = "archive"
        elif "condensed" in url:
            typeOfVideo = "condensed"
        elif "highlights" in url:
            typeOfVideo = "highlights"
   
    #Load the list of games
    gameList = pickle.load(open(os.path.join(ADDON_PATH_PROFILE, 'games'),"rb"))
   
    
    linkList = []
   
    #Get the url of the game
    for game in gameList:
        if game[1] in url:            
            #Add teamnames and game title to the list
            title = game[0]
            homeTeam = game[2]
            awayTeam = game[3]
            linkList = [title, [homeTeam, awayTeam]]
            game_id = game[5]
           
            #Quality settings            
            if QUALITY == 4 or 'bestquality' in url:
                if int(year) >= 2014:
                    quality = '_5000'
                else:
                    quality = ''
            elif '5000K' in url:
                quality = '_5000'
            elif QUALITY == 3 or '4500K' in url:
                if int(year) >= 2014:
                    quality = '_5000'
                elif int(year) >= 2012:
                    quality = '_4500'
                else:
                    quality = '_3000'
            elif QUALITY == 2 or '3000K' in url:
                quality = '_3000'
            elif QUALITY == 1 or '1600K' in url:
                quality = '_1600'
            else:
                quality = '_800'
           
            #Get the HLS stream
            playPath = game[4][37:][:-49]
            http_url = "http://nhl.cdn.neulion.net/" + playPath[4:] + "/v1/playlist" + quality + ".m3u8"            
            http_url = http_url.replace('/pc/', '/ced/')
            
           
            #Fix for 2012-2013 season
            if int(year) >= 2012:
                http_url = http_url.replace('http://nhl.cdn.neulion.net/', 'http://nlds150.cdnak.neulion.com/')
                http_url = http_url.replace('s/nhlmobile/vod/nhl/', 'nlds_vod/nhl/vod/')
                #Fix issue for some people who don't seem to get 'condensed' in the org url.
                if typeOfVideo == 'archive' and http_url.find('condensed') == -1:
                    http_url = http_url.replace('/v1/playlist', 'condensed')                
                http_url = http_url.replace('/v1/playlist', '')
                http_url = http_url.replace('.m3u8', '_ced.mp4.m3u8')
 
                #Fix for early games in the season
                http_url = http_url.replace('condensed_ced', 'condensed_1_ced')
                http_url = http_url.replace('condensed_5000', 'condensed_1_5000')
                http_url = http_url.replace('condensed_4500', 'condensed_1_4500')
                http_url = http_url.replace('condensed_3000', 'condensed_1_3000')
                http_url = http_url.replace('condensed_1600', 'condensed_1_1600')
                http_url = http_url.replace('condensed_800', 'condensed_1_800')
 
                #Fix for some streams
                http_url = http_url.replace('s/as3/', '')
               
               # print "BEFORE SWITCH === " + http_url
 
                if typeOfVideo == 'archive':                    
                    http_url = http_url.replace('condensed', 'whole')
                    http_url = http_url.replace('condensed', 'whole')
                    http_url = http_url.replace('_ced.mp4', '_ipad.mp4')
                elif typeOfVideo == 'highlights':
                    http_url = http_url.replace('condensed', 'continuous')
           
           
            home_url = http_url
            away_url = http_url.replace('_h_', '_a_')

            date_for_url = datetime.fromtimestamp(time.mktime(time.strptime(game[0][0:10],xbmc.getRegion('dateshort')))).strftime("%Y-%m-%d")            
            game_info = getGameInfo(date_for_url,game_id)

            #Home url
            linkList.append([LOCAL_STRING(31320), home_url])
            
            #Check if Away Video is available           
            if game_info != '':                
                print game_info['gameHighlightVideo']['hasArchiveAwayVideo']
                if game_info['gameHighlightVideo']['hasArchiveAwayVideo']:           
                    #Away url
                    linkList.append([LOCAL_STRING(31330), away_url])


            #Check if French Video is available
            if game_info != '':
                #French flag stored in live (NHL Bug???)
                print game_info['gameLiveVideo']['hasLiveFrenchVideo']
                if game_info['gameLiveVideo']['hasLiveFrenchVideo']:
                    #French url            
                    ########################################
                    # This code / logic is used from TB123's code
                    ########################################
                    # Somehow Montreal French feed is switched between home and away for 2014 season (NHL bug???)
                    if (int(year) == 2014 and home_url != None and awayTeam == 'MON'):
                        away_home = "_%s_%s_" % (awayTeam.lower(), homeTeam.lower())
                        home_away = "_%s_%s_" % (homeTeam.lower(), awayTeam.lower())

                        away_home = away_home.replace('mon','mtl')
                        home_away =  home_away.replace('mon','mtl')
                        home_url = home_url.replace(away_home, home_away)
                    ########################################
                    french_url = home_url.replace('/nhl/', '/nhlfr/')
                    french_url = french_url.replace('_h_', '_fr_')
                    french_url = french_url.replace('_5000_','_3000_')
                    french_url = french_url.replace('_4500_','_3000_')
                    linkList.append(['French', french_url])
 
            #French streams (experimental)
            #print home_url
            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2014/11/08/205/2_205_min_mtl_1415_fr_whole_1_5000_ipad.mp4.m3u8
            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2014/10/09/8/2_8_mtl_wsh_1415_fr_whole_1_3000_ipad.mp4.m3u8
            #French streams (experimental)

            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2014/11/08/205/2_205_min_mtl_1415_fr_whole_1_iphone.mp4.m3u8?nltid=nhlgc&nltdt=7&nltnt=1&uid=741758&hdnea=expires%3D1415556549%7Eaccess%3D%2Fnlds_vod%2Fnhlfr%2Fvod%2F2014%2F11%2F08%2F205%2F*%7Emd5%3D6cec36469ae2ff0a5d27fc47cf31a2da HTTP/1.1
            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2014/11/08/205/2_205_min_mtl_1415_h_whole_1_5000_ipad.mp4.m3u8
            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2014/11/08/205/2_205_min_mtl_1415_fr_whole_1_5000_ipad.mp4.m3u8]

            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2014/11/05/185/2_185_det_nyr_1415_fr_whole_1_3000_ipad.mp4.m3u8
            #GOOD ONE
            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2014/11/05/184/2_184_buf_mtl_1415_fr_whole_1_3000_ipad.mp4.m3u8
            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2013/12/29/586/2_586_fla_mtl_1314_fr_whole_1_ipad.mp4.m3u8
            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2013/12/29/586/2_586_mtl_fla_1314_fr_whole_1_ipad.mp4.m3u8
            #MINE
            #http://nlds150.cdnak.neulion.com/nlds_vod/nhlfr/vod/2014/11/05/184/2_184_mtl_buf_1415_fr_whole_1_1600_ipad.mp4.m3u8
            """            
            if homeTeam == 'MON' or homeTeam == 'OTT':
                home_url = home_url.replace('/nhl/', '/nhlfr/')
                #home_url = home_url.replace('nlds138', 'nlds60')
                home_url = home_url.replace('_h_','_fr_')
                home_url = home_url.replace('_5000_','_3000_')
                home_url = home_url.replace('_4500_','_3000_')
                linkList.append([LOCAL_STRING(31340), home_url])
            if awayTeam == 'MON' or awayTeam == 'OTT':
                away_url = away_url.replace('/nhl/', '/nhlfr/')
                #away_url = away_url.replace('nlds138', 'nlds60')
                away_url = away_url.replace('_a_','_fr_')
                away_url = away_url.replace('_2_','_1_')
                away_url = away_url.replace('_5000_','_3000_')
                away_url = away_url.replace('_4500_','_3000_')
                linkList.append([LOCAL_STRING(31340), away_url])
            """          
 
            break
   
    return linkList
