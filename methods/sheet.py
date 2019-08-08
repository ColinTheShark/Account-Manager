import re
from string import ascii_lowercase

import gspread
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

STEAMID_REGEX = re.compile(r'\d{17}')


class Sheet:
    def __init__(self, sheet_key: str, credentials: str,
                 url_col: str, ban_col: str):
        """Set up the Communication with your Spreadsheet.

        Parameters
        ~~~~~~~~~~

        sheet_key (`str`):
            The Sheet Key from the URL.

        credentials (`str`):
            The filename of the downloaded credentials.

        url_col (`str`):
            The indicator of the Column Letter for the profile URLs.

        ban_col (`str`):
            The indicator of the column letter for the game ban counter.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials, SCOPE)
        self.url_col = url_col
        self.ban_col = ban_col

        gc = gspread.authorize(credentials)
        self.sheet = gc.open_by_key(sheet_key).sheet1

    def get_profile_links(self):
        col = ascii_lowercase.index(self.url_col.lower())
        cells = self.sheet.col_values(col)[5:]
        return [
            c.value
            for c
            in self.sheet.range(
                '{0}6:{0}{1}'.format(
                    self.url_col.upper(),
                    1+len(cells)
                )
            )
        ]

    def update_profiles(self, players: list):
        steam_ids = [
            int(STEAMID_REGEX.search(x).group(0))
            for x
            in self.get_profile_links()
        ]

        players = sorted(players,
                         key=lambda player: steam_ids.index(player.steam_id))

        col = self.ban_col
        game_bans = self.sheet.range('{0}6:{0}{1}'.format(
            col, str(5 + len(steam_ids))))

        for player, game_ban in zip(players, game_bans):
            game_ban.value = player.number_of_game_bans

        return self.sheet.update_cells(game_bans)
