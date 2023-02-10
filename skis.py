# parsing and searching stuff
import numpy as np
import tqdm
from craigslist import CraigslistForSale as cl
import os
import time
import pandas as pd
import pickle
import urllib3

# email stuff
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, ssl, email
import pathlib
import datetime
import warnings

LOCATIONS = {
    'Alabama': {'auburn': 'auburn', 'bham': 'birmingham', 'dothan': 'dothan', 'shoals': 'florence / muscle shoals', 'gadsden': 'gadsden-anniston', 'huntsville': 'huntsville / decatur', 'mobile': 'mobile', 'montgomery': 'montgomery', 'tuscaloosa': 'tuscaloosa'}, 'Alaska': {'anchorage': 'anchorage / mat-su', 'fairbanks': 'fairbanks', 'kenai': 'kenai peninsula', 'juneau': 'southeast alaska'}, 'Arizona': {'flagstaff': 'flagstaff / sedona', 'mohave': 'mohave county', 'phoenix': 'phoenix', 'prescott': 'prescott', 'showlow': 'show low', 'sierravista': 'sierra vista', 'tucson': 'tucson', 'yuma': 'yuma'}, 'Arkansas': {'fayar': 'fayetteville ', 'fortsmith': 'fort smith', 'jonesboro': 'jonesboro', 'littlerock': 'little rock', 'texarkana': 'texarkana'}, 'California': {'bakersfield': 'bakersfield', 'chico': 'chico', 'fresno': 'fresno / madera', 'goldcountry': 'gold country', 'hanford': 'hanford-corcoran', 'humboldt': 'humboldt county', 'imperial': 'imperial county', 'inlandempire': 'inland empire', 'losangeles': 'los angeles', 'mendocino': 'mendocino county', 'merced': 'merced', 'modesto': 'modesto', 'monterey': 'monterey bay', 'orangecounty': 'orange county', 'palmsprings': 'palm springs', 'redding': 'redding', 'sacramento': 'sacramento', 'sandiego': 'san diego', 'sfbay': 'san francisco bay area', 'slo': 'san luis obispo', 'santabarbara': 'santa barbara', 'santamaria': 'santa maria', 'siskiyou': 'siskiyou county', 'stockton': 'stockton', 'susanville': 'susanville', 'ventura': 'ventura county', 'visalia': 'visalia-tulare', 'yubasutter': 'yuba-sutter'}, 'Colorado': {'boulder': 'boulder', 'cosprings': 'colorado springs', 'denver': 'denver', 'eastco': 'eastern CO', 'fortcollins': 'fort collins / north CO', 'rockies': 'high rockies', 'pueblo': 'pueblo', 'westslope': 'western slope'}, 'Connecticut': {'newlondon': 'eastern CT', 'hartford': 'hartford', 'newhaven': 'new haven', 'nwct': 'northwest CT'}, 'Delaware': {'delaware': 'delaware'}, 'District of Columbia': {'washingtondc': 'washington'}, 'Florida': {'daytona': 'daytona beach', 'keys': 'florida keys', 'fortlauderdale': 'fort lauderdale', 'fortmyers': 'ft myers / SW florida', 'gainesville': 'gainesville', 'cfl': 'heartland florida', 'jacksonville': 'jacksonville', 'lakeland': 'lakeland', 'lakecity': 'north central FL', 'ocala': 'ocala', 'okaloosa': 'okaloosa / walton', 'orlando': 'orlando', 'panamacity': 'panama city', 'pensacola': 'pensacola', 'sarasota': 'sarasota-bradenton', 'miami': 'south florida', 'spacecoast': 'space coast', 'staugustine': 'st augustine', 'tallahassee': 'tallahassee', 'tampa': 'tampa bay area', 'treasure': 'treasure coast'}, 'Georgia': {'albanyga': 'albany ', 'athensga': 'athens', 'atlanta': 'atlanta', 'augusta': 'augusta', 'brunswick': 'brunswick', 'columbusga': 'columbus ', 'macon': 'macon / warner robins', 'nwga': 'northwest GA', 'savannah': 'savannah / hinesville', 'statesboro': 'statesboro', 'valdosta': 'valdosta'}, 'Hawaii': {'honolulu': 'hawaii'}, 'Idaho': {'boise': 'boise', 'eastidaho': 'east idaho', 'lewiston': 'lewiston / clarkston', 'twinfalls': 'twin falls'}, 'Illinois': {'bn': 'bloomington-normal', 'chambana': 'champaign urbana', 'chicago': 'chicago', 'decatur': 'decatur', 'lasalle': 'la salle co', 'mattoon': 'mattoon-charleston', 'peoria': 'peoria', 'rockford': 'rockford', 'carbondale': 'southern illinois', 'springfieldil': 'springfield ', 'quincy': 'western IL'}, 'Indiana': {'bloomington': 'bloomington', 'evansville': 'evansville', 'fortwayne': 'fort wayne', 'indianapolis': 'indianapolis', 'kokomo': 'kokomo', 'tippecanoe': 'lafayette / west lafayette', 'muncie': 'muncie / anderson', 'richmondin': 'richmond ', 'southbend': 'south bend / michiana', 'terrehaute': 'terre haute'}, 'Iowa': {'ames': 'ames', 'cedarrapids': 'cedar rapids', 'desmoines': 'des moines', 'dubuque': 'dubuque', 'fortdodge': 'fort dodge', 'iowacity': 'iowa city', 'masoncity': 'mason city', 'quadcities': 'quad cities', 'siouxcity': 'sioux city', 'ottumwa': 'southeast IA', 'waterloo': 'waterloo / cedar falls'}, 'Kansas': {'lawrence': 'lawrence', 'ksu': 'manhattan', 'nwks': 'northwest KS', 'salina': 'salina', 'seks': 'southeast KS', 'swks': 'southwest KS', 'topeka': 'topeka', 'wichita': 'wichita'}, 'Kentucky': {'bgky': 'bowling green', 'eastky': 'eastern kentucky', 'lexington': 'lexington', 'louisville': 'louisville', 'owensboro': 'owensboro', 'westky': 'western KY'}, 'Louisiana': {'batonrouge': 'baton rouge', 'cenla': 'central louisiana', 'houma': 'houma', 'lafayette': 'lafayette', 'lakecharles': 'lake charles', 'monroe': 'monroe', 'neworleans': 'new orleans', 'shreveport': 'shreveport'}, 'Maine': {'maine': 'maine'}, 'Maryland': {'annapolis': 'annapolis', 'baltimore': 'baltimore', 'easternshore': 'eastern shore', 'frederick': 'frederick', 'smd': 'southern maryland', 'westmd': 'western maryland'}, 'Massachusetts': {'boston': 'boston', 'capecod': 'cape cod / islands', 'southcoast': 'south coast', 'westernmass': 'western massachusetts', 'worcester': 'worcester / central MA'}, 'Michigan': {'annarbor': 'ann arbor', 'battlecreek': 'battle creek', 'centralmich': 'central michigan', 'detroit': 'detroit metro', 'flint': 'flint', 'grandrapids': 'grand rapids', 'holland': 'holland', 'jxn': 'jackson ', 'kalamazoo': 'kalamazoo', 'lansing': 'lansing', 'monroemi': 'monroe ', 'muskegon': 'muskegon', 'nmi': 'northern michigan', 'porthuron': 'port huron', 'saginaw': 'saginaw-midland-baycity', 'swmi': 'southwest michigan', 'thumb': 'the thumb', 'up': 'upper peninsula'}, 'Minnesota': {'bemidji': 'bemidji', 'brainerd': 'brainerd', 'duluth': 'duluth / superior', 'mankato': 'mankato', 'minneapolis': 'minneapolis / st paul', 'rmn': 'rochester ', 'marshall': 'southwest MN', 'stcloud': 'st cloud'}, 'Mississippi': {'gulfport': 'gulfport / biloxi', 'hattiesburg': 'hattiesburg', 'jackson': 'jackson', 'meridian': 'meridian', 'northmiss': 'north mississippi', 'natchez': 'southwest MS'}, 'Missouri': {'columbiamo': 'columbia / jeff city', 'joplin': 'joplin', 'kansascity': 'kansas city', 'kirksville': 'kirksville', 'loz': 'lake of the ozarks', 'semo': 'southeast missouri', 'springfield': 'springfield', 'stjoseph': 'st joseph', 'stlouis': 'st louis'}, 'Montana': {'billings': 'billings', 'bozeman': 'bozeman', 'butte': 'butte', 'greatfalls': 'great falls', 'helena': 'helena', 'kalispell': 'kalispell', 'missoula': 'missoula', 'montana': 'eastern montana'}, 'Nebraska': {'grandisland': 'grand island', 'lincoln': 'lincoln', 'northplatte': 'north platte', 'omaha': 'omaha / council bluffs', 'scottsbluff': 'scottsbluff / panhandle'}, 'Nevada': {'elko': 'elko', 'lasvegas': 'las vegas', 'reno': 'reno / tahoe'}, 'New Hampshire': {'nh': 'new hampshire'}, 'New Jersey': {'cnj': 'central NJ', 'jerseyshore': 'jersey shore', 'newjersey': 'north jersey', 'southjersey': 'south jersey'}, 'New Mexico': {'albuquerque': 'albuquerque', 'clovis': 'clovis / portales', 'farmington': 'farmington', 'lascruces': 'las cruces', 'roswell': 'roswell / carlsbad', 'santafe': 'santa fe / taos'}, 'New York': {'albany': 'albany', 'binghamton': 'binghamton', 'buffalo': 'buffalo', 'catskills': 'catskills', 'chautauqua': 'chautauqua', 'elmira': 'elmira-corning', 'fingerlakes': 'finger lakes', 'glensfalls': 'glens falls', 'hudsonvalley': 'hudson valley', 'ithaca': 'ithaca', 'longisland': 'long island', 'newyork': 'new york city', 'oneonta': 'oneonta', 'plattsburgh': 'plattsburgh-adirondacks', 'potsdam': 'potsdam-canton-massena', 'rochester': 'rochester', 'syracuse': 'syracuse', 'twintiers': 'twin tiers NY/PA', 'utica': 'utica-rome-oneida', 'watertown': 'watertown'}, 'North Carolina': {'asheville': 'asheville', 'boone': 'boone', 'charlotte': 'charlotte', 'eastnc': 'eastern NC', 'fayetteville': 'fayetteville', 'greensboro': 'greensboro', 'hickory': 'hickory / lenoir', 'onslow': 'jacksonville ', 'outerbanks': 'outer banks', 'raleigh': 'raleigh / durham / CH', 'wilmington': 'wilmington', 'winstonsalem': 'winston-salem'}, 'North Dakota': {'bismarck': 'bismarck', 'fargo': 'fargo / moorhead', 'grandforks': 'grand forks', 'nd': 'north dakota'}, 'Ohio': {'akroncanton': 'akron / canton', 'ashtabula': 'ashtabula', 'athensohio': 'athens ', 'chillicothe': 'chillicothe', 'cincinnati': 'cincinnati', 'cleveland': 'cleveland', 'columbus': 'columbus', 'dayton': 'dayton / springfield', 'limaohio': 'lima / findlay', 'mansfield': 'mansfield', 'sandusky': 'sandusky', 'toledo': 'toledo', 'tuscarawas': 'tuscarawas co', 'youngstown': 'youngstown', 'zanesville': 'zanesville / cambridge'}, 'Oklahoma': {'lawton': 'lawton', 'enid': 'northwest OK', 'oklahomacity': 'oklahoma city', 'stillwater': 'stillwater', 'tulsa': 'tulsa'}, 'Oregon': {'bend': 'bend', 'corvallis': 'corvallis/albany', 'eastoregon': 'east oregon', 'eugene': 'eugene', 'klamath': 'klamath falls', 'medford': 'medford-ashland', 'oregoncoast': 'oregon coast', 'portland': 'portland', 'roseburg': 'roseburg', 'salem': 'salem'}, 'Pennsylvania': {'altoona': 'altoona-johnstown', 'chambersburg': 'cumberland valley', 'erie': 'erie', 'harrisburg': 'harrisburg', 'lancaster': 'lancaster', 'allentown': 'lehigh valley', 'meadville': 'meadville', 'philadelphia': 'philadelphia', 'pittsburgh': 'pittsburgh', 'poconos': 'poconos', 'reading': 'reading', 'scranton': 'scranton / wilkes-barre', 'pennstate': 'state college', 'williamsport': 'williamsport', 'york': 'york'}, 'Rhode Island': {'providence': 'rhode island'}, 'South Carolina': {'charleston': 'charleston', 'columbia': 'columbia', 'florencesc': 'florence', 'greenville': 'greenville / upstate', 'hiltonhead': 'hilton head', 'myrtlebeach': 'myrtle beach'}, 'South Dakota': {'nesd': 'northeast SD', 'csd': 'pierre / central SD', 'rapidcity': 'rapid city / west SD', 'siouxfalls': 'sioux falls / SE SD', 'sd': 'south dakota'}, 'Tennessee': {'chattanooga': 'chattanooga', 'clarksville': 'clarksville', 'cookeville': 'cookeville', 'jacksontn': 'jackson  ', 'knoxville': 'knoxville', 'memphis': 'memphis', 'nashville': 'nashville', 'tricities': 'tri-cities'}, 'Texas': {'abilene': 'abilene', 'amarillo': 'amarillo', 'austin': 'austin', 'beaumont': 'beaumont / port arthur', 'brownsville': 'brownsville', 'collegestation': 'college station', 'corpuschristi': 'corpus christi', 'dallas': 'dallas / fort worth', 'nacogdoches': 'deep east texas', 'delrio': 'del rio / eagle pass', 'elpaso': 'el paso', 'galveston': 'galveston', 'houston': 'houston', 'killeen': 'killeen / temple / ft hood', 'laredo': 'laredo', 'lubbock': 'lubbock', 'mcallen': 'mcallen / edinburg', 'odessa': 'odessa / midland', 'sanangelo': 'san angelo', 'sanantonio': 'san antonio', 'sanmarcos': 'san marcos', 'bigbend': 'southwest TX', 'texoma': 'texoma', 'easttexas': 'tyler / east TX', 'victoriatx': 'victoria ', 'waco': 'waco', 'wichitafalls': 'wichita falls'}, 'Utah': {'logan': 'logan', 'ogden': 'ogden-clearfield', 'provo': 'provo / orem', 'saltlakecity': 'salt lake city', 'stgeorge': 'st george'}, 'Vermont': {'vermont': 'vermont'}, 'Virginia': {'charlottesville': 'charlottesville', 'danville': 'danville', 'fredericksburg': 'fredericksburg', 'norfolk': 'hampton roads', 'harrisonburg': 'harrisonburg', 'lynchburg': 'lynchburg', 'blacksburg': 'new river valley', 'richmond': 'richmond', 'roanoke': 'roanoke', 'swva': 'southwest VA', 'winchester': 'winchester'}, 'Washington': {'bellingham': 'bellingham', 'kpr': 'kennewick-pasco-richland', 'moseslake': 'moses lake', 'olympic': 'olympic peninsula', 'pullman': 'pullman / moscow', 'seattle': 'seattle-tacoma', 'skagit': 'skagit / island / SJI', 'spokane': "spokane / coeur d'alene", 'wenatchee': 'wenatchee', 'yakima': 'yakima'}, 'West Virginia': {'charlestonwv': 'charleston ', 'martinsburg': 'eastern panhandle', 'huntington': 'huntington-ashland', 'morgantown': 'morgantown', 'wheeling': 'northern panhandle', 'parkersburg': 'parkersburg-marietta', 'swv': 'southern WV', 'wv': 'west virginia (old)'}, 'Wisconsin': {'appleton': 'appleton-oshkosh-FDL', 'eauclaire': 'eau claire', 'greenbay': 'green bay', 'janesville': 'janesville', 'racine': 'kenosha-racine', 'lacrosse': 'la crosse', 'madison': 'madison', 'milwaukee': 'milwaukee', 'northernwi': 'northern WI', 'sheboygan': 'sheboygan', 'wausau': 'wausau'}, 'Wyoming': {'wyoming': 'wyoming'}
}

THIS_PATH = pathlib.Path(__file__).parent.absolute()
DATA_PATH = '{}/data/results_skis.pickle'.format(THIS_PATH)

def get_locs(states=None, locs=None):
    if states is None and locs is None:
        states = LOCATIONS.keys()
    if states is not None:
        locs = []
        for state in states:
            locs += list(LOCATIONS[state].keys())
    return locs

def search_for_rhodes(states=None, locs=None, query='rhodes', category='msa', posted_today=False, header=None):
    locs = get_locs(states, locs)

    res = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")        
        for loc in tqdm.tqdm(locs, desc=header):
            res += list(cl(loc, filters={'query': query, 'posted_today': posted_today}, category=category).get_results())    
    return res

def update_local_dictionary(d, search):
    new = []
    for r in search:
        if r['id'] not in d:
            new.append(r['id'])
            d[r['id']] = r
    return d, new

def update_saved_dictionary(d, path):
    with open(path, 'wb') as handle:
        pickle.dump(d, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return 0

def load_saved_dictionary(path):
    if os.path.exists(path):
        with open(path, 'rb') as handle:
            data = pickle.load(handle)
        return data
    return {}

def search_loop(states=None, locs=None, query='rhodes piano', category='msa', posted_today=False, path=None, header=None):
    if path is None:
        path = DATA_PATH

    data = load_saved_dictionary(path)
    res = search_for_rhodes(states, locs, query, category, posted_today, header=header)
    data, new = update_local_dictionary(data, res)
    
    ret = None
    if len(new) > 0:
        ret = pd.DataFrame([data[r] for r in new]).set_index('id')
    
    return ret, data, path

def send_email(df, server):
    me = "bobisloaded@gmail.com"
    you = "luclepot@berkeley.edu"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "{} new skis found".format(len(df))
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).
    html = MIMEText(df.to_html(), 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(html)

    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    server.sendmail(me, you, msg.as_string())

    return 0

def setup_email_server(port, gmail_uname):
    password = input('password please: ')
    return port, "{}@gmail.com".format(gmail_uname), password, ssl.create_default_context()

def search_header(i, st):
    return 'SEARCH {} :: {}'.format(i, datetime.datetime.fromtimestamp(st).strftime('%m/%d/%Y, %H:%M:%S EST :'))

def main(port=465, uname='bobisloaded', wait_time=3600):

    port, myemail, password, context = setup_email_server(port, uname)
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(myemail, password)
        sleep_time = -1
        i = 1
        while(True):
            try:
                if sleep_time > 0:
                    time.sleep(sleep_time)            
                start_time = time.time()

                new, data, path = search_loop(
                    ['California', 'Oregon', 'Michigan',
                    'Nevada', 'Arizona', 'Utah', 'Idaho', 'Washington'],
                    header=search_header(i, start_time), query='shift binding skis'
                )
                if new is not None:
                    send_email(new, server)
                    update_saved_dictionary(data, path)
                del data
                del new
                end_time = time.time()
                sleep_time = wait_time - (end_time - start_time)
                i += 1
            except urllib3.exceptions.ProtocolError:
                print('FAILED, retrying')

if __name__ == '__main__':
    main()
