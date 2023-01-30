import anki
import aqt
from aqt import mw
from datetime import datetime
from anki.hooks import addHook, wrap
from aqt.deckbrowser import DeckBrowser

from .config import getUserOption, writeConfig

def generateStats():
	totalreviews = mw.col.db.scalar("""select count(id) from revlog""")
	totalreviews = str(totalreviews)
	
	time = mw.col.db.first("""select sum(time) from revlog""")
	ttime = time if time != None else 0
	if ttime != 0:	
		ttime = str(int(str(ttime).replace("(","").replace("[","").replace("]","").replace(")","").replace(",","").replace("None","0")))
		tunits = {'hours': 3600000, 'days': 86400000, 'weeks': 604800000, 'minutes': 60000}
		t_unit = getUserOption('time_unit')
		if t_unit not in tunits:
			t_unit = 'hours'	
			
		ttime = int(ttime)/(tunits[t_unit])
	
	styling = f"""
"font-family: {getUserOption('fontfamily')};
font-size: {getUserOption('fontsize')};
color: {getUserOption('color')};
"""
	if getUserOption('bold'):
		styling += " font-weight: bold;"
		
	if not getUserOption('custom_text_styling'):
		styling = f"""
			"
			"""


	styling += '"'
	sep = getUserOption('thousand_separator')
	
	if totalreviews == "0":
		string = f"<span style={styling}><br/>No reviews done yet</span>"
	else:
		before = "Studied "
		total_reviews = '{:,}'.format(int(totalreviews)).replace(',', sep)
		middle = " cards in "
		total_time = '{:,.2f}'.format(ttime).replace(',', sep)
		middle2 = " "
		after = " total"
		string = f"<span style={styling}><br/>{before}{total_reviews}{middle}{total_time}{middle2}{t_unit}{after}</span>"
	return string

def renderStats(self, _old):
	return _old(self) + generateStats()

def db_wrc(deck_browser, content):
	content.stats += generateStats()

## code taken from somebody else, who?
# for some reason it works offline, but not when adding it via ankiweb(order in which the plugin loads, probably)
# honestly no clue what this does but it fixes this problem, thanks glutanimate??
try:
	from aqt.gui_hooks import deck_browser_will_render_content
	deck_browser_will_render_content.append(db_wrc)
except (ImportError, ModuleNotFoundError):
	DeckBrowser._renderStats = wrap(DeckBrowser._renderStats, renderStats, 'around')

