class Answer:
    def __init__(self, date):
        self.date = date
        self.classic = None
        self.quote = None
        self.ability = None
        self.abilityKeyPress = None
        self.emoji = None
        self.splash = None
        self.splashName = None

    def set(self, mode, val):
        match mode:
            case "classic":
                self.classic = val
            case "quote":
                self.quote = val
            case "ability":
                self.ability = val[0]
                self.abilityKeyPress = val[1]
            case "emoji":
                self.emoji = val
            case "splash":
                self.splash = val[0]
                self.splashName = val[1]

    def pretty_print(self):
        return f'''Answers: 
            Date: {self.date}
            Classic: {self.classic}
            Quote: {self.quote}
            Ability: {self.ability} \t Ability Key: {self.abilityKeyPress}
            Emoji: {self.emoji}
            Splash: {self.splash} \t Splash Name: {self.splashName}
        '''
                