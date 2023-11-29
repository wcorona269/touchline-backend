from app.models import FavoriteType

post_seeds = [
    "Messi and Ronaldo could score blindfolded, change my mind.",
    "VAR has a secret crush on controversy. It just can't stay away.",
    "Waiting for the day Neymar gets an Oscar for his acting skills on the pitch.",
    "Referees must attend Hogwarts because their decision-making is pure magic.",
    "Soccer conspiracy theory: the ball is actually a magnet, and goalkeepers have metal gloves.",
    "If diving was an Olympic sport, soccer players would dominate the podium.",
    "Did you hear? The grass complained that Messi walks on it too much.",
    "Soccer players' second job: professional grass testers.",
    "Breaking: Ronaldo challenges gravity and wins. Again.",
    "VAR's favorite song: 'I Will Survive' by Gloria Gaynor.",
    "Soccer players' secret talent: finding invisible defenders to trip over.",
    "If only my life had as many plot twists as a soccer match.",
    "Can we replace corner flags with selfie sticks? Asking for a friend.",
    "Soccer goalkeepers must have cat DNA. Their reflexes are unreal.",
    "Messi's left foot: sponsored by wizardry since 2003.",
    "In an alternate universe, soccer matches are decided by dance-offs.",
    "I believe in aliens because no human can dribble like Messi and be from this planet.",
    "Ronaldo's hairstylist deserves a Nobel Prize for defying gravity.",
    "Referees be like: 'Foul? What foul?'",
    "Soccer players' favorite book: '101 Ways to Fall Dramatically.'",
    "If diving was an art form, soccer players would be the Picassos of the sports world.",
    "Messi's dribbling skills are so good; even the ball gets confused.",
    "Soccer players' fitness secret: chasing after the referee's decisions.",
    "Rumors say Cristiano Ronaldo's abs have their own fan club.",
    "When life gives you lemons, pretend they're soccer balls and score a goal.",
    "Plot twist: the offside rule was invented by goalkeepers to get a break.",
    "Who needs superheroes when we have soccer players defying physics every match?",
    "I've seen better tackles in a game of Twister.",
    "Soccer players' life motto: 'If you can't win, trip someone.'",
    "I'm convinced soccer balls are made of pure magic. How else do they bend like Beckham?",
    "Why run a marathon when you can watch a soccer match with 90 minutes of non-stop drama?",
    "I bet aliens play soccer with black holes as goals.",
    "Soccer players' pre-game ritual: practicing their Oscar acceptance speeches.",
    "Messi's penalty kicks: breaking goalkeepers' hearts since forever.",
    "Ronaldo's goal celebrations: sponsored by confetti companies worldwide.",
    "If soccer was easy, it would be called knitting. #SoccerLife",
    "Breaking: scientists discover soccer players' secret teleportation skills during dribbles.",
    "I'm not saying soccer players are magicians, but have you seen their disappearing acts during fouls?",
    "Soccer players' favorite movie: 'The Matrix' because dodging tackles is an art.",
    "If diving was a profession, soccer players would be CEOs.",
    "I'm starting to believe soccer balls have GPS. How else do they find the net every time?",
    "Rumors say Ronaldo's hair gel contains the secrets of the universe.",
    "Soccer players' favorite board game: Twister, because flexibility is key.",
    "If I had a dollar for every dramatic fall in soccer, I'd be richer than Messi.",
    "Do soccer players attend drama school before joining the team?",
    "I have 99 problems, and watching soccer solves all of them.",
    "Plot twist: soccer matches are actually auditions for action movie stunt doubles.",
    "In an alternate universe, soccer matches are decided by the best hair flick.",
    "I've seen more spins in a soccer match than a DJ at a nightclub. #SoccerVibes",
]

user_seeds = [
    ['willyc', 'wcorona269@gmail.com',
        'Passionate soccer enthusiast and goal scorer. Ready to conquer the field!', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/zizouUCL.jpg'],
    ['spennybluntz', 'spencer@gmail.com',
        'Dribbling through life with a soccer ball. Let the games begin!', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/zlatan.jpg'],
    ['ancelottireignsupereme', 'goalgetter@example.com',
        'Chasing dreams one goal at a time. Soccer is not just a game, it’s a way of life.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/ancelotti.jpg'],
    ['cristianocentre', 'soccerfanatic@example.com',
        'Cheering for my favorite teams, living for the beautiful game. ⚽', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/cristiano.jpg'],
    ['BeautifulDelBosque', 'kickmaster@example.com',
        'Mastering the art of kicking and scoring goals. Soccer is my forte.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/DelBosque.jpg'],
    ['UtdMan', 'goalgalaxy@example.com',
        'Lost in the galaxy of goals. Join me in the soccer universe!', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/fellaini.jpg'],
    ['superjack', 'dribbleking@example.com',
        'Dribbling skills that mesmerize. On a mission to conquer the soccer kingdom.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/grealish.jpeg'],
    ['lewanGOALski', 'netripper@example.com', "Ripping the nets apart with powerful shots. Goalkeeper's nightmare!", 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/lewa.jpeg'],
    ['YungKylian', 'tikitakapro@example.com',
        'Precision passing, tactical brilliance. Tiki-taka is my mantra.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/mbappe.jpeg'],
    ['goat_enjoyer', 'futbolfever@example.com',
        'Feverishly passionate about futbol. Living and breathing the game.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/messiBDOR.jpg'],
    ['JobabonitoBaby', 'soccersniper@example.com',
        'Sniping goals from a distance. Precision and accuracy define my game.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/messithumbsup.jpeg'],
    ['mr_maradona', 'cornerflagchamp@example.com',
        'Claiming victory, one corner flag at a time. Soccer champ in the making.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/messiWC.jpeg'],
    ['the_special_one', 'stadiumroarer@example.com',
        'Roaring in the stadiums, supporting my team with all my heart.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/mourinho.jpg'],
    ['come_to_brazil', 'crazyforgoals@example.com',
        'Crazy, passionate, and obsessed with goals. Scoring is my addiction.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/neymar.jpg'],
    ['SoccerWizard', 'soccerwizard@example.com',
        'Magical moves and wizardry on the field. Turning soccer into an art form.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/neymarPSG.jpeg'],
    ['the_Maestro', 'goalhoarder@example.com',
        'Holding onto goals like treasures. Hoarding the glory, one goal at a time.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/pele.jpeg'],
    ['GuardiolaGene', 'dribblemaestro@example.com', "Maestro of dribbling skills. Dancing through defenders like they're not there.", 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/pep.jpg'],
    ['UCL_warrior', 'netninja@example.com',
        'Ninja-like reflexes guarding the net. Keeping the opponents at bay with precision saves.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/pepUCL.jpg'],
    ['BeautifulBarca', 'freekickmagician@example.com',
        'Magical free kicks that bend the rules of physics. Watch and be amazed!', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/ronaldinho.jpg'],
    ['realronaldofans9', 'soccersorcerer@example.com',
        'Sorcerer on the soccer field, casting spells with every touch.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/Ronaldo9.jpg'],
    ['TheGoalHunter199', 'thegoalhunter@example.com',
        'Hunting down goals, relentless in my pursuit of victory. Join me on the hunt!', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/ronaldosmile.jpg'],
    ['FergieTime', 'soccersupernova@example.com',
        'A supernova of talent and passion, exploding onto the soccer scene.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/SAF.jpg'],
    ['UTDbeliever', 'pitchprowler@example.com',
        'Prowling the pitch, dominating every inch. Fear my presence on the field.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/SAFRonny.jpg'],
    ['egyptian_prince', 'soccerswagger@example.com',
        'Swaggering through the soccer world with style and confidence.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/salah.jpeg'],
    ['golazo_genius', 'stadiumsultan@example.com',
        'Ruling the stadiums like a sultan. Commanding respect with every goal scored.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/suarez.jpg'],
    ['lebron_of_soccer', 'goalgladiator@example.com',
        'Gladiator in the arena of goals. Battling opponents, emerging victorious.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/USA.jpeg'],
    ['WengerKnowledge', 'soccermaestro@example.com',
        'Maestro of the soccer world. Every move orchestrated to perfection.', 'https://touchlinedevstorage.blob.core.windows.net/touchline-dev-pics/wenger.jpg'],
]

favorite_seeds = [
    ['Manchester City', FavoriteType.CLUB, 50],
    ['Real Madrid', FavoriteType.CLUB, 541],
    ['Barcelona', FavoriteType.CLUB, 529],
    ['UEFA Champions League', FavoriteType.LEAGUE, 2],
    ['Premier League', FavoriteType.LEAGUE, 39],
    ['La Liga', FavoriteType.LEAGUE, 140],
    ['Bundesliga', FavoriteType.LEAGUE, 78],
    ['Ligue 1', FavoriteType.LEAGUE, 61],
    ['E. Haaland', FavoriteType.PLAYER, 1100],
    ['R. Lewandowski', FavoriteType.PLAYER, 521]
]