import re

class LoldleData:
    def __init__(self):
        self.classic = None
        self.quote = None
        self.ability = None
        self.abilityKey = False
        self.emoji = None
        self.splash = None
        self.splashName = False

    def parse_loldle_submission(self, content):
    # Define a pattern to capture the mode names, their scores, and checkmark status (if ✓ is present)
        pattern = (r"Classic: (?P<classic>\d+)|"
                r"Quote: (?P<quote>\d+)|"
                r"Ability: (?P<ability>\d+)(?P<ability_check> ✓)?|"
                r"Emoji: (?P<emoji>\d+)|"
                r"Splash: (?P<splash>\d+)(?P<splash_check> ✓)?")
        
        for match in re.finditer(pattern, content):
            if match.group('classic'):
                self.classic = int(match.group('classic'))
            if match.group('quote'):
                print("quote")
                self.quote = int(match.group('quote'))
            if match.group('ability'):
                print("ability")
                self.ability = int(match.group('ability'))
                self.abilityKey = True if match.group('ability_check') else False 
            if match.group('emoji'):
                print("emoji")
                self.emoji = int(match.group('emoji'))
            if match.group('splash'):
                self.splash = int(match.group('splash'))
                self.splashName = True if match.group('splash_check') else False

    def is_valid_submission(self):
        if (
            self.classic == None or
            self.quote == None or
            self.ability == None or
            self.emoji == None or
            self.splash == None
         ):
            return False
        return True