# mfl_playoff_leagues/src/mfl_playoff_leagues/mfl.py
# -*- coding: utf-8 -*-
# Copyright (C) 2022 Eric Truett
# Licensed under the MIT License

import datetime
import os
import re
from typing import Dict, List

import pytz
import requests


class Table:
    @staticmethod
    def make_table_row(values: List[str], tag: str) -> str:
        """Makes html rows from header values"""
        parts = [f'<{tag}>{value}</{tag}>' for value in values]
        return f'<tr>{"".join(parts)}</tr>'
    

    @staticmethod
    def make_table(data: List[dict], caption: str, headers: List[str], body_id: str = 'table-body-id') -> str:
        """Makes an HTML table from a data structure
        
        Args:
            data (List[dict]): the table data, list of dict
            caption (str): the table caption 
            headers (List[str]): the table header names
            body_id (str): the table body id, default 'table-body-id'
        
        Returns:
            str - HTML table
            
        """
        header_row = make_table_row(headers, 'th')
        table_rows = '\n'.join([make_table_row(list(item.values()), 'td') for item in data])
        
        return f"""
            <table>
            <caption>
            <span classname="module_expand" class="module_expand" href="javascript:void(0);">[-]</span>
            <span>{caption}</span>
            </caption>
            <thead>
            {header_row}    
            </thead>
            <tbody id='{body_id}'>
            {table_rows}
            </tbody>
            </table>
        """   

    @staticmethod
    def parse_unix_timestamp(ts):
        """Parses unix timestamp and converts to string with Chicago timezone"""
        dt = datetime.datetime.utcfromtimestamp(int(ts)).replace(tzinfo=pytz.UTC)
        return dt.astimezone(pytz.timezone('America/Chicago')).strftime("%Y-%m-%d %H:%M:%S")


class MFL:
    """Class to handle get / parse data from MFL API"""
    
    def __init__(self, year: str, league: str):
        self.league = league
        self.year = year
        self.s = requests.Session()
        self.s.headers.update(self._cookie_headers())
        self.url = f'https://www73.myfantasyleague.com/{self.year}/export'
        self.base_params = {'L': league, 'JSON': '1'}
        self._franchise_data = None
        self._player_data = None
        self._live_scoring_data = None
        
    def _cookie_headers(self):           
        """Gets headers with authentication cookie
        
        Args:
            None
            
        Returns:
            None
            
        """
        user = os.getenv('MFL_USERNAME')
        pwd = os.getenv('MFL_PASSWORD')
        auth_url = f'https://api.myfantasyleague.com/{self.year}/login?USERNAME={user}&PASSWORD={pwd}&XML=1'
        r = self.s.get(auth_url)
        patt = 'MFL_USER_ID="(.*?)["]+' 
        match = re.search(patt, r.text) 
        cookie_value = match.group(1) 
        return {'Cookie': f'MFL_USER_ID={cookie_value}'}

    def get(self, params: dict = None, headers: dict = None) -> requests.Response:
        """Gets resource"""
        params = {**self.base_params, **params} if params else self.base_params.copy()
        return self.s.get(self.url, params=params, headers=headers)
 
    # MFL ENDPOINTS
    def get_league(self) -> requests.Response:
        """Gets league"""
        return self.get(params={'TYPE': 'league'})

    def get_league_standings(self) -> requests.Response:
        """Gets league"""
        return self.get(params={'TYPE': 'leagueStandings'})

    def get_live_scoring(self, week: str = '') -> requests.Response:
        """Gets live scoring results"""
        return self.get(params={'TYPE': 'liveScoring', 'W': week})

    def get_nfl_schedule(self, week: str = '') -> requests.Response:
        """Gets weekly NFL schedule"""
        return self.get(params={'TYPE': 'nflSchedule', 'W': week})
        
    def get_player_scores(self, week: str = '', year: str = '') -> requests.Response:
        """Gets player scoring for given week"""
        return self.get(params={'TYPE': 'playerScores', 'W': week, 'YEAR': year})
    
    def get_players(self, details: str = '0') -> requests.Response:
        """Gets player scoring for given week"""
        return self.get(params={'TYPE': 'players', 'DETAILS': details})

    def get_points_allowed(self) -> requests.Response:
        """Gets team points allowed by position"""
        return self.get(params={'TYPE': 'pointsAllowed'})

    def get_projected_scores(self, week: str = '') -> requests.Response:
        """Gets projected player scoring for given week"""
        return self.get(params={'TYPE': 'projectedScores', 'W': week})
    
    def get_weekly_results(self, week: str = '') -> requests.Response:
        """Gets weekly scoring resource for given week"""
        return self.get(params={'TYPE': 'weeklyResults', 'W': week})
    
    # PARSE MFL ENDPOINTS   
    def parse_league(self, r: requests.Response, filters: tuple = ('id', 'name', 'owner_name', 'lastVisit')) -> Dict[str, dict]:
        """Gets the base manager data for a league
        
        Args:
            r (requests.Response): the API response
            
        Returns:
            Dict[str, dict]: key is the franchise_id, value is the full franchise dict
         
        """       
        # assemble the data
        data = {}  
        for row in r.json()['league']['franchises']['franchise']:
            d = {k: row[k] for k in filters}
            d['lastVisit'] = Table.parse_unix_timestamp(d['lastVisit'])
            data[d['id']] = d
        return data

    def parse_league_standings(self) -> dict:
        """parses league"""
        return data

    def parse_live_scoring(self, week: str = '') -> dict:
        """parses live scoring results"""
        return data

    def parse_nfl_schedule(self, week: str = '') -> dict:
        """parses weekly NFL schedule"""
        return data
        
    def parse_player_scores(self, week: str = '', year: str = '') -> dict:
        """parses player scoring for given week"""
        return data
    
    def parse_players(self, details: str = '0') -> dict:
        """parses player scoring for given week"""
        return data

    def parse_points_allowed(self) -> dict:
        """parses team points allowed by position"""
        return data

    def parse_projected_scores(self, week: str = '') -> dict:
        """parses projected player scoring for given week"""
        return data
    
    def parse_weekly_results(self, week: str = '') -> dict:
        """parses weekly scoring resource for given week"""
        return data

    
    # utility functions
    def get_player(self, pid) -> dict:
        """Returns player dict given player id"""
        return self.player_data.get(pid)
   
    @property
    def live_scoring_data(self):
        """Gets live scoring"""
        
        # return cached value if set
        if self._live_scoring_data:
            return self._live_scoring_data
        
        # will need franchise player data for lookup
        franchises = self.franchise_data
        players = self.player_data
        
        # make API call
        r = self.get(params={'TYPE': 'liveScoring'})
        
        # assemble the data
        data = []   
        
        # loop over the franchise
        franchises = []
        for row in data.json()['liveScoring']['franchise']:
            franchise = l.get(row['id'])
            franchises.append({
              'franchise_name': franchise['name'],
              'manager_name': franchise['owner_name'],
              'players': [m.parse_live_scoring_player(player) for player in row['players']['player']]
            })
        
        
        # return list of dict
        self._live_scoring_data = franchises
        return self._live_scoring_data
 
    @property
    def franchise_data(self) -> Dict[str, dict]:
        """Gets the base manager data for a league
        
        Args:
            None
            
        Returns:
            Dict[str, dict]: key is the franchise_id, value is the full franchise dict
         
        """
        # return cached value if set
        if self._franchise_data:
            return self._franchise_data
       
        # make API call
        r = self.get(params={'TYPE': 'league'})
        
        # assemble the data
        filters = ('id', 'name', 'owner_name', 'lastVisit')
        data = {}  
        for row in r.json()['league']['franchises']['franchise']:
            d = {k: row[k] for k in filters}
            d['lastVisit'] = Table.parse_unix_timestamp(d['lastVisit'])
            data[d['id']] = d
        
        # return list of dict
        self._franchise_data = data
        return self._franchise_data

    @property
    def player_data(self) -> Dict[str, dict]:
        """Gets the player data for a league
        
        Args:
            None
            
        Returns:
            Dict[str, dict]: key is the player_id, value is the full player dict
            
        """
        # return cached value if set
        if self._player_data:
            return self._player_data

       # make API call
        r = self.get(params={'TYPE': 'players'})

        # assemble the data
        self._player_data = {item['id']: item for item in r.json()['players']['player']}
        return self._player_data
    
    def parse_live_scoring_player(self, d):
        """Parses player dict from live_scoring endpoint

        Args:
            d (dict): the player dict

        Returns:
            dict

        """
        wanted = ('id', 'name', 'team', 'position', 'score', 'gameSecondsRemaining')
        pid = d['id']
        comb = {**m.get_player(pid), **d}
        return {k: comb[k] for k in wanted}
    

