# all the imports
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import requests

import soco

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
#    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#['_SoCo__get_radio_favorites', '__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', 
# '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', 
# '__str__', '__subclasshook__', '__weakref__', '_all_zones', '_groups', '_is_bridge', '_is_coordinator', '_parse_zone_group_state', 
# '_player_name', '_uid', '_visible_zones', '_zgs_cache', 'add_to_queue', 'add_uri_to_queue', 'all_groups', 'all_zones', 'avTransport', 
# 'bass', 'clear_queue', 'contentDirectory', 'cross_fade', 'deviceProperties', 'get_album_artists', 'get_albums', 
# 'get_artists', 'get_composers', 'get_current_track_info', 'get_current_transport_info', 'get_favorite_radio_shows', 
# 'get_favorite_radio_stations', 'get_genres', 'get_group_coordinator', 'get_music_library_information', 'get_playlists', 'get_queue', 
# 'get_sonos_playlists', 'get_speaker_info', 'get_speakers_ip', 'get_tracks', 'group', 'ip_address', 'is_bridge', 'is_coordinator', 
# 'is_visible', 'join', 'loudness', 'mute', 'next', 'partymode', 'pause', 'play', 'play_from_queue', 'play_mode', 'play_uri', 'player_name', 
# 'previous', 'remove_from_queue', 'renderingControl', 'seek', 'speaker_info', 'speaker_ip', 'status_light', 'stop', 
# 'switch_to_line_in', 'switch_to_tv', 'treble', 'uid', 'unjoin', 'visible_zones', 'volume', 'zoneGroupTopology']


def convertJsonDictionaryDates(jsondictionary):
    #import pdp; pdb.trace()
    items = []
    try:
        for item in jsondictionary:
            for k in item.keys():

                if isinstance(item[k], dict):
                    item[k] = self.convertJsonDictionaryDates(jsondictionary=[item[k]])[0]
                else:
                    #\\/Date\((-?\d+)\)\\/

                    p = re.compile('/Date\(')
                    m = p.match(str(item[k]))
                    if m:
                        item[k] = datetime.datetime(1970, 1, 1) \
                            + datetime.timedelta(milliseconds=int(re.findall(r'\d+'
                                , item[k])[0])) \
                            + datetime.timedelta(hours=int((re.findall(r'\d+'
                                , item[k])[1])[:2]))
            items.append(item)
    except Exception, e:
        pass
    return items

def getJsonDate(date):
    init_date = datetime.datetime(1970, 1, 1)

    if type(date) is not datetime.datetime:
        logger.warning('Invalid date! %s' % str(date))
        return None
    else:
        delta = date - init_date
        day_part = delta.days * 86400 * 1000
        second_part = delta.seconds * 1000
        microsecond_part = delta.microseconds / 1000

        total = day_part + second_part + microsecond_part
        jsondate = '/Date(' + str(total) + '+0200)/'

    return jsondate

@app.route('/')
def show_players():
    #players = [dict(player_name=player.player_name) for player in soco.discover()]
    players = list(soco.discover())
    programid = request.args.get('programid', '')
    page = request.args.get('page', '1')
    paginate = request.args.get('paginate', 'false')

    pods = []
    pagination = {}

    if programid:
        req = requests.get('http://api.sr.se/api/v2/podfiles?programid=%s&page=%s&format=json&pagination=%s' % (programid, page, paginate))
        progs = req.json()
        
        pagination = progs.get('pagination', {})
        pod_files = progs.get('podfiles')
        pods = [dict(title=pod_file.get('title', ''), url=pod_file.get('url', ''), publishdateutc=pod_file.get('publishdateutc', '')) for pod_file in pod_files]
        #import pdb; pdb.set_trace()

    print pods
    return render_template('show_players.html', players=players, pods=pods, pagination=pagination, pages=dict(page=page, nextpage=int(page)+1, previouspage=int(page)-1), programid=programid)



@app.route('/play_uri', methods=['POST'])
def play_uri():
    ip = request.args.get('ip', '')
    uri = request.form['uri']

    sonos = soco.SoCo(ip)

    sonos.play_uri(uri)
    flash('Playing...')
    return redirect(url_for('show_players'))

@app.route('/set_volume')
def set_volume():
    ip = request.args.get('ip', '')
    direction = request.args.get('direction', '')

    sonos = soco.SoCo(ip)

    volume = sonos.volume

    if direction == 'up':
        sonos.volume = volume + 1
        flash('Volume increased')
    else:
        sonos.volume = volume - 1
        flash('Volume decreased')

    return redirect(url_for('show_players'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

