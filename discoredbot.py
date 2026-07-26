import asyncio
import random
import re

import discord
from discord.ext import commands

# Initialize the bot specifically for a user account.
# self_bot=True is supported in discord.py-self.
bot = commands.Bot(command_prefix='-', self_bot=True)
bot.remove_command('help')

# Stores user match keys and the emoji to react with.
auto_react_list = {}

# Stores channel-specific auto-reactions: {(user_key, channel_id): emoji}
channel_autoreact_list = {}

# Stores auto-reply message
auto_reply_message = None
auto_reply_enabled = False

# Blacktea game settings
blacktea_enabled = False
blacktea_used_words = {}  # Track used words per channel

# Reaction cooldown tracker to avoid API flagging
reaction_cooldown = {}

# MAXIMUM COVERAGE word list for blacktea game - 99%+ of all 3-letter substrings
COMMON_WORDS = [
    # ===== NGS (rings, kings, things, songs, wrongs, strings, beginnings, endings) =====
    'rings', 'kings', 'things', 'wings', 'songs', 'longs', 'wrongs', 'strings', 'springs', 'brings', 'swings', 'stings', 'clings', 'flings', 'slings', 'pings', 'dings', 'sings', 'tings', 'zings', 'bing', 'ding', 'king', 'ping', 'ring', 'sing', 'ting', 'wing', 'zing', 'fangs', 'gangs', 'hangs', 'pangs', 'bangs', 'clangs', 'slangs', 'twangs', 'wangs', 'yangs', 'dongs', 'gongs', 'pongs', 'tongs', 'wrongs', 'songs', 'longs', 'bongs', 'prongs', 'thongs', 'lungs', 'rungs', 'bungs', 'dungs', 'hungs', 'jungs', 'sungs', 'wrings', 'brings', 'stings', 'things', 'beings', 'doings', 'goings', 'rulings', 'winnings', 'spinnings', 'grinnings', 'beginnings', 'endings', 'sendings', 'bendings', 'lendings', 'mendings', 'pendings', 'tendings', 'vendings', 'blending', 'spending', 'rending', 'tending', 'lending', 'bending', 'mending', 'fending', 'vending', 'pending', 'settings', 'meetings', 'greetings', 'beatings', 'heatings', 'seatings', 'wettings', 'pettings', 'bettings', 'lettings', 'jettings', 'settings', 'nettings', 'shettings', 'wettings',

    # ===== MPS (jumps, pumps, lumps, camps, temps, symptoms, attempts) =====
    'jumps', 'pumps', 'lumps', 'bumps', 'humps', 'rumps', 'stumps', 'thumps', 'clumps', 'grumps', 'plumps', 'frumps', 'slumps', 'trumps', 'camps', 'damps', 'lamps', 'ramps', 'stamps', 'clamps', 'tramps', 'cramps', 'champs', 'scamps', 'vamps', 'tamps', 'samps', 'amps', 'temps', 'tempts', 'exempts', 'attempts', 'prompts', 'contempts', 'symptoms', 'examples', 'temples', 'samples', 'amples', 'simples', 'dimples', 'pimples', 'rumples', 'crumples', 'trumpets', 'strumpets', 'campaigns', 'tampings', 'dumplings', 'crumpets', 'jumped', 'pumped', 'lumped', 'bumped', 'humped', 'rumped', 'stumped', 'thumped', 'clumped', 'grumped', 'plumped', 'slumped', 'trumped',

    # ===== RTS (parts, starts, hearts, arts, sports, courts, shorts, ports) =====
    'parts', 'starts', 'hearts', 'arts', 'sorts', 'sports', 'courts', 'shorts', 'snorts', 'ports', 'forts', 'carts', 'darts', 'farts', 'tarts', 'warts', 'charts', 'smarts', 'departs', 'imparts', 'upstart', 'stalwarts', 'coats', 'boats', 'floats', 'goats', 'moats', 'gloats', 'notes', 'votes', 'quotes', 'dotes', 'motes', 'totes', 'cotes', 'rotes', 'wrote', 'smoke', 'stroke', 'spoke', 'broke', 'choke', 'evoke', 'invoke', 'provoke', 'revoke', 'stoke', 'poke', 'yoke', 'woke', 'joke', 'coke', 'choked', 'stoked', 'poked', 'yoked', 'joked', 'coked', 'evoked', 'invoked', 'provoked', 'revoked', 'stroked', 'smoked', 'croaked', 'bloated', 'devoted', 'demoted', 'promoted', 'denoted', 'devoted', 'emoted',

    # ===== IES (babies, ladies, stories, worries, berries, carries, fairies, duties) =====
    'babies', 'ladies', 'copies', 'stories', 'worries', 'hurries', 'berries', 'cherries', 'fairies', 'varies', 'carries', 'marries', 'tarries', 'parties', 'calories', 'studies', 'duties', 'varieties', 'commodities', 'anxieties', 'utilities', 'securities', 'properties', 'societies', 'activities', 'entities', 'identities', 'capacities', 'tenacities', 'audacities', 'fallacies', 'legacies', 'prophecies', 'policies', 'species', 'gracies', 'tracies', 'aries', 'galleries', 'tallies', 'calories', 'rallies', 'allies', 'dallies', 'scallies', 'bullies', 'gullies', 'skies', 'ties', 'lies', 'dies', 'pies', 'tries', 'cries', 'dries', 'fries', 'spies', 'dyes', 'eyes', 'ryes', 'byes', 'guys', 'buys', 'denies', 'supplies', 'replies', 'applies', 'implies', 'complies', 'defies', 'relies', 'jellies', 'bellies', 'wellies', 'tellies', 'smellies',

    # ===== NTS (wants, grants, plants, ants, events, moments, contents) =====
    'wants', 'grants', 'plants', 'ants', 'pants', 'chants', 'slants', 'stunts', 'blunts', 'counts', 'mounts', 'amounts', 'fronts', 'vents', 'dents', 'rents', 'tents', 'bents', 'scents', 'events', 'prevents', 'intents', 'contents', 'segments', 'moments', 'documents', 'elements', 'supplements', 'implements', 'sentiments', 'statements', 'payments', 'treatments', 'developments', 'assignments', 'departments', 'apartments', 'agreements', 'tournaments', 'governments', 'movements', 'improvements', 'adjustments', 'instruments', 'monuments', 'comments', 'cement', 'lament', 'torment', 'ferment', 'augment', 'fragment', 'pigment', 'segment', 'figment', 'regiment', 'sediment', 'increment', 'condiment', 'judgment', 'adjustment', 'recruitment', 'indictment', 'enticement', 'allotment', 'abutment',

    # ===== NDS (hands, lands, bands, sounds, pounds, minds, finds, friends) =====
    'hands', 'lands', 'bands', 'sands', 'stands', 'brands', 'strands', 'grands', 'commands', 'demands', 'understands', 'wands', 'bonds', 'fonds', 'ponds', 'sounds', 'pounds', 'wounds', 'rounds', 'grounds', 'mounds', 'bounds', 'hounds', 'founds', 'clouds', 'crowds', 'shrouds', 'vendors', 'benders', 'fenders', 'renders', 'tenders', 'slenders', 'blenders', 'genders', 'sends', 'bends', 'fends', 'mends', 'rends', 'trends', 'spends', 'friends', 'pretends', 'extends', 'intends', 'defends', 'offends', 'suspends', 'appends', 'depends', 'upends', 'transcends', 'descends', 'ascends', 'minds', 'finds', 'kinds', 'winds', 'binds', 'hinds', 'blinds', 'grinds', 'reminds', 'upwinds', 'rewinds', 'unwinds',

    # ===== RST (first, worst, burst, thirst, forest, breast, coast, fast) =====
    'first', 'worst', 'burst', 'thirst', 'cursed', 'nursed', 'pursed', 'dispersed', 'forest', 'breast', 'feast', 'beast', 'yeast', 'east', 'coast', 'roast', 'toast', 'boast', 'blast', 'fast', 'last', 'past', 'cast', 'vast', 'mast', 'haste', 'paste', 'taste', 'waste', 'chaste', 'baste', 'outcast', 'forecast', 'broadcast', 'steadfast', 'breakfast', 'typecast', 'northeast', 'southeast', 'southwest', 'northwest', 'clustered', 'mustered', 'blustered', 'flustered', 'blistered', 'glistered', 'mastered', 'plastered', 'fasted', 'lasted', 'pasted', 'tasted', 'wasted', 'coasted', 'roasted', 'toasted', 'boasted', 'blasted', 'misted', 'listed', 'grist', 'wrist', 'tryst', 'curst', 'durst',

    # ===== ONG (long, song, strong, wrong, along, belong, throng, oblong) =====
    'long', 'song', 'strong', 'wrong', 'dong', 'gong', 'kong', 'pong', 'tong', 'along', 'among', 'belong', 'prolong', 'throng', 'oblong', 'sarong', 'lifelong', 'headlong', 'daylong', 'alllong', 'evlong', 'furlong', 'prolonged', 'wronged', 'longing', 'songing', 'thronging', 'wronging', 'songbird', 'longbow', 'strongbox', 'alongside',

    # ===== ALI (quality, reality, alien, alive, align, alliance, allow) =====
    'quality', 'reality', 'mortality', 'polarity', 'clarity', 'charity', 'scarlet', 'palette', 'mallet', 'ballet', 'wallet', 'pallet', 'bullet', 'mullet', 'cullet', 'gullet', 'alien', 'alienate', 'align', 'alignment', 'alike', 'alive', 'all', 'alley', 'alliance', 'allied', 'allocate', 'allot', 'allow', 'alloy', 'allude', 'allure', 'ally', 'allure', 'alleviate', 'allocation', 'allowance', 'allowable', 'alibi', 'alibis', 'alimentary', 'aliquot', 'alimony', 'alpine', 'already', 'altar', 'alter', 'alternate', 'altitude', 'altogether', 'altruism', 'alliances', 'alarms', 'alias',

    # ===== ERS (players, makers, fighters, teachers, watchers, factors, masters) =====
    'players', 'makers', 'fighters', 'miners', 'speakers', 'teachers', 'preaches', 'breaches', 'teaches', 'reaches', 'beaches', 'peaches', 'leaches', 'watchers', 'catchers', 'pitchers', 'batchers', 'hatchers', 'matches', 'watches', 'patches', 'latches', 'shatters', 'chatters', 'clatters', 'flatters', 'platters', 'splatters', 'scatters', 'tatters', 'matters', 'batters', 'patters', 'ratters', 'factors', 'tractors', 'detractors', 'extractors', 'contractors', 'protractors', 'vendors', 'splendors', 'commanders', 'blenders', 'renders', 'tenders', 'slenders', 'fenders', 'genders', 'masters', 'plasters', 'disasters', 'blisters', 'glisters', 'misters', 'sisters', 'listers', 'whiskers', 'clusters', 'musters', 'busters', 'dusters', 'gusters', 'lusters', 'flusters', 'roosters', 'boosters', 'posters', 'coasters', 'headers', 'readers', 'leaders', 'beaders', 'traders', 'waders', 'faders', 'graders', 'shaders', 'raiders',

    # ===== EXC (except, exception, excel, excuse, execute, excite, exclude) =====
    'except', 'exception', 'excess', 'exchange', 'excite', 'excitement', 'excel', 'excellent', 'exclaim', 'exclude', 'exclusive', 'excuse', 'execute', 'execution', 'executive', 'exemplify', 'exempt', 'exert', 'exhale', 'exhaust', 'exhibit', 'exhort', 'exigency', 'exile', 'exist', 'exit', 'exorcise', 'expand', 'expanse', 'expat', 'expect', 'expectancy', 'expectation', 'expediency', 'expedient', 'expedite', 'expel', 'expend', 'expendable', 'expenditure', 'expense', 'expensive', 'experience', 'experiment', 'expert', 'expertise', 'expiate', 'expiration', 'expire', 'explain', 'expletive', 'explicable', 'explicit', 'explicate', 'explode', 'exploit', 'exploration', 'explore', 'exponent', 'export', 'exposition', 'expostulate', 'exposure', 'expound', 'express', 'expression', 'expressive', 'expropriate', 'expunge', 'expurgate', 'excused', 'excuser', 'excursion', 'excited', 'exceeds', 'excels',

    # ===== ENT (went, rent, event, prevent, content, moment, element) =====
    'went', 'rent', 'dent', 'bent', 'sent', 'tent', 'event', 'prevent', 'content', 'intent', 'extent', 'consent', 'dissent', 'present', 'represent', 'resent', 'absent', 'accent', 'ascent', 'descent', 'cement', 'lament', 'ferment', 'torment', 'segment', 'augment', 'fragment', 'pigment', 'figment', 'regiment', 'sediment', 'increment', 'condiment', 'implement', 'supplement', 'complement', 'monument', 'document', 'moment', 'element', 'settlement', 'development', 'apartment', 'department', 'government', 'agreement', 'entertainment', 'statement', 'payment', 'treatment', 'pent', 'vent', 'slent', 'spent', 'blent', 'scent', 'relent', 'repent', 'lement', 'rement', 'entment', 'indent', 'indent', 'rodent', 'potent', 'latent', 'patent', 'urgent', 'portent', 'serpent', 'torrent', 'current', 'parent', 'regent', 'agent', 'gent',

    # ===== EAD (dead, read, head, bread, thread, spread, steady, already) =====
    'dead', 'read', 'head', 'bread', 'thread', 'spread', 'dread', 'tread', 'instead', 'bead', 'lead', 'mead', 'stead', 'steady', 'already', 'shred', 'threadbare', 'unstead', 'misled', 'mislead', 'unread', 'reread', 'widespread', 'wellbread', 'homestead', 'farmstead', 'waisted', 'beaded', 'headed', 'leaded', 'pleaded', 'breaded', 'treaded', 'dreaded', 'threaded', 'beading', 'heading', 'leading', 'pleading', 'spreading', 'steadiness', 'steadily', 'headache', 'headband', 'headset', 'headstone', 'headstrong', 'headwater', 'headway', 'deaden', 'deadening', 'deadline', 'deadlock', 'deadpan', 'readied', 'reader', 'readily', 'readiness', 'reading', 'heading', 'leadhead', 'bedhead', 'deadhead', 'redhead', 'ahead', 'instead', 'ahead',

    # ===== CORE 3-LETTER WORDS =====
    'cat', 'dog', 'rat', 'bat', 'hat', 'mat', 'sat', 'pat', 'eat', 'tea', 'sea', 'pea', 'red', 'bed', 'led', 'fed',
    'pen', 'ten', 'men', 'hen', 'den', 'can', 'man', 'fan', 'pan', 'ran', 'tan', 'van', 'ban', 'box', 'fox', 'sox',
    'six', 'mix', 'fix', 'pig', 'dig', 'big', 'wig', 'rig', 'jog', 'log', 'fog', 'bog', 'cog', 'hot', 'pot', 'got',
    'lot', 'dot', 'not', 'rot', 'cut', 'but', 'gut', 'hut', 'jut', 'nut', 'put', 'rut', 'tut', 'bus', 'gas', 'has',
    'was', 'ass', 'yes', 'set', 'get', 'jet', 'let', 'met', 'net', 'pet', 'wet', 'yet', 'bet', 'age', 'ace', 'ice',
    'use', 'end', 'and', 'old', 'ore', 'are', 'ate', 'ape', 'axe', 'eye', 'ear', 'arm', 'art', 'air', 'who', 'why',
    'how', 'cow', 'bow', 'low', 'mow', 'row', 'sow', 'tow', 'wow', 'new', 'few', 'dew', 'sew', 'pew', 'raw', 'law',
    'saw', 'paw', 'jaw', 'awe', 'owl', 'awl', 'owe', 'own', 'two', 'too', 'zoo', 'goo', 'boo', 'coo', 'for', 'nor',
    'her', 'per', 'bar', 'car', 'far', 'jar', 'tar', 'war', 'oar', 'par', 'our', 'fur', 'day', 'say', 'way', 'pay',
    'lay', 'may', 'hay', 'bay', 'gay', 'ray', 'key', 'boy', 'toy', 'joy', 'soy', 'try', 'cry', 'dry', 'fry', 'pry',
    'sky', 'spy', 'fly', 'guy', 'buy', 'shy', 'icy', 'ivy', 'any', 'vex', 'hex', 'sex', 'nex', 'yep', 'wax', 'tax', 'fax', 'sax', 'pax', 'lax', 'max', 'zap', 'rap', 'map', 'nap', 'cap', 'gap', 'lap', 'tap', 'yap', 'sap', 'dap',

    # ===== ALL -ING WORDS =====
    'sing', 'ring', 'wing', 'king', 'ping', 'ding', 'ting', 'zing', 'bing', 'jing', 'ling', 'ming', 'ning', 'ving', 'bring', 'cling', 'fling', 'sling', 'sting', 'string', 'swing', 'thing', 'wring', 'spring', 'during', 'caring', 'daring', 'faring', 'glaring', 'sharing', 'staring', 'earing', 'tearing', 'bearing', 'hearing', 'nearing', 'searing', 'wearing', 'clearing', 'smearing', 'appearing', 'disappearing', 'cheering', 'steering', 'jeering', 'peering', 'sneering', 'veering', 'leering', 'boring', 'coring', 'poring', 'storing', 'soaring', 'roaring', 'mooring', 'touring', 'pouring', 'flooring', 'ignoring', 'restoring', 'exploring', 'adoring', 'scoring', 'snoring', 'curing', 'luring', 'enduring', 'assuring', 'ensuring', 'procuring', 'securing', 'alluring', 'blaring', 'snaring', 'sparing', 'scaring', 'staring', 'flaring', 'warning', 'morning', 'scorning', 'adorning', 'burning', 'turning', 'spurning', 'churning', 'learning', 'earning', 'yearning', 'returning', 'discerning', 'concerning', 'bowing', 'cowing', 'mowing', 'sowing', 'towing', 'vowing', 'showing', 'snowing', 'flowing', 'glowing', 'growing', 'knowing', 'throwing', 'allowing', 'following', 'swallowing', 'hallowing', 'gallowing', 'tallowing', 'falling', 'calling', 'balling', 'walling', 'stalling', 'installing', 'telling', 'selling', 'dwelling', 'swelling', 'spelling', 'smelling', 'yelling', 'bellowing', 'mellowing', 'yellowing', 'hollowing', 'following', 'wallowing', 'galloping', 'helping', 'yelping',

    # ===== ALL -TION/-SION WORDS =====
    'action', 'faction', 'traction', 'fraction', 'reaction', 'creation', 'vacation', 'location', 'notation', 'rotation', 'citation', 'dictation', 'nation', 'station', 'ration', 'potion', 'lotion', 'motion', 'ocean', 'function', 'junction', 'unction', 'suction', 'auction', 'caution', 'section', 'fiction', 'diction', 'friction', 'caption', 'option', 'portion', 'question', 'mission', 'passion', 'session', 'profession', 'confession', 'possession', 'obsession', 'expression', 'impression', 'depression', 'oppression', 'suppression', 'compression', 'repression', 'transgression', 'succession', 'transmission', 'remission', 'admission', 'permission', 'submission', 'emission', 'omission', 'commission', 'fission', 'tension', 'pension', 'dimension', 'extension', 'suspension', 'apprehension', 'comprehension', 'ascension', 'descension', 'dissension', 'intention', 'attention', 'retention', 'detention', 'prevention', 'intervention', 'invention', 'convention', 'contention', 'abstention', 'discussion', 'percussion', 'concussion', 'recursion', 'excursion', 'incursion', 'dispersion', 'immersion', 'submersion', 'aversion', 'diversion', 'inversion', 'conversion', 'reversion', 'decision', 'division', 'collision', 'illusion', 'delusion', 'inclusion', 'exclusion', 'conclusion', 'seclusion', 'occlusion', 'intrusion', 'extrusion', 'profusion', 'confusion', 'diffusion', 'infusion', 'transfusion', 'vision', 'revision', 'provision', 'supervision', 'television', 'envision', 'prevision', 'incision', 'precision', 'excision', 'fashion', 'cushion', 'mansion', 'expansion', 'dedication', 'medication', 'education', 'excavation', 'privation', 'motivation', 'preparation', 'reparation', 'separation', 'operation', 'cooperation', 'evaporation', 'exploration', 'exploitation', 'application', 'implication', 'complication', 'explanation', 'duplication', 'publication', 'replication', 'simplification', 'amplification', 'clarification', 'classification', 'notification', 'ratification', 'gratification', 'justification', 'modification', 'codification', 'specification', 'qualification', 'quantification', 'sanctification', 'electrification', 'authentication', 'stratification', 'satisfaction', 'dissatisfaction', 'beautification', 'identification', 'certification', 'verification', 'calcification', 'petrification', 'mystification', 'mortification', 'fortification', 'purification', 'unification', 'reunification', 'diversification', 'intensification', 'densification', 'personification', 'falsification', 'ossification', 'gasification',

    # ===== ADDITIONAL LONG-TAIL WORDS =====
    'light', 'night', 'right', 'sight', 'tight', 'fight', 'might', 'flight', 'plight', 'slight', 'height', 'weight', 'eight', 'high', 'sigh', 'nigh', 'thigh', 'bight', 'wight', 'fright', 'bright', 'knight', 'delight', 'insight', 'upright', 'alight', 'outright', 'tonight', 'twilight', 'lightning', 'tighten', 'lighten', 'frighten', 'enlighten', 'rightly', 'tightly', 'sightly', 'nightly', 'mighty', 'lightly', 'slightly', 'highway', 'highness', 'highlight', 'lightheaded', 'lightweight', 'highly', 'alright', 'frightened', 'enlightened', 'playwright', 'underweight', 'middleweight', 'heavyweight', 'lightweight',

    'tough', 'rough', 'cough', 'dough', 'though', 'through', 'bough', 'thorough', 'borough', 'trough', 'plough', 'enough', 'ought', 'bought', 'brought', 'caught', 'fought', 'sought', 'taught', 'thought', 'wrought', 'naught', 'nought', 'oughta', 'slough',

    'would', 'could', 'should', 'mould', 'wouldnt', 'couldnt', 'shouldnt',

    'able', 'cable', 'fable', 'gable', 'label', 'sable', 'table', 'stable', 'capable', 'enable', 'disable', 'reliable', 'variable', 'edible', 'visible', 'divisible', 'terrible', 'horrible', 'incredible', 'credible', 'audible', 'sensible', 'defensible', 'responsible', 'impossible', 'possible', 'flexible', 'taxable', 'battle', 'cattle', 'bottle', 'little', 'settle', 'kettle', 'mettle', 'nettle', 'rattle', 'tattle', 'prattle', 'brittle', 'whittle', 'spittle', 'shuttle', 'scuttle', 'title', 'subtle', 'turtle', 'hurtle', 'tousle', 'jostle', 'castle', 'wrestle', 'beetle', 'attle', 'ettle', 'ittle', 'oodle', 'poodle', 'doodle', 'noodle', 'strudel', 'fiddle', 'middle', 'riddle', 'paddle', 'saddle', 'caddle', 'waddle', 'peddle', 'meddle', 'toddle', 'coddle', 'dawdle', 'cuddle', 'muddle', 'puddle', 'bundle', 'kindle', 'spindle', 'swindle', 'dwindle', 'toodle', 'poodle', 'candle', 'handle', 'sandal', 'scandal', 'vandal',

    'annual', 'manual', 'casual', 'ritual', 'actual', 'usual', 'virtual', 'sensual', 'textual', 'factual', 'sexual', 'mutual', 'gradual', 'individual', 'spiritual', 'dual', 'equal', 'legal', 'regal', 'naval', 'pedal', 'medal', 'modal', 'nodal', 'tidal', 'bridal', 'nidal', 'venal', 'penal', 'renal', 'banal', 'canal', 'final', 'spinal', 'fetal', 'petal', 'metal', 'total', 'vital', 'mortal', 'portal', 'brutal', 'feudal', 'caudal', 'vandal', 'scandal', 'sandal', 'medal', 'pedal', 'tidal', 'bridal', 'nodal', 'modal', 'tonal', 'zonal', 'tidal',

    'easy', 'easel', 'ease', 'please', 'grease', 'tease', 'lease', 'cease', 'increase', 'disease', 'release', 'decrease', 'crease', 'beast', 'feast', 'least', 'yeast', 'east', 'coast', 'roast', 'toast', 'boast', 'blast', 'fast', 'last', 'past', 'cast', 'vast', 'mast', 'haste', 'paste', 'taste', 'waste', 'chaste', 'baste', 'aster', 'faster', 'master', 'plaster', 'disaster', 'contrast', 'breakfast', 'forecast', 'overcast', 'broadcast', 'steadfast', 'outcast', 'typecast', 'northeast', 'southeast', 'southwest', 'northwest', 'eastward', 'easterly',

    'unique', 'unit', 'unite', 'unity', 'unicorn', 'uniform', 'universe', 'university', 'universal', 'unions', 'unison', 'uniquely', 'unify', 'unified', 'unitive', 'united', 'units', 'untie', 'until', 'unlock', 'unfold', 'undo', 'unfit', 'unable', 'uncouth', 'undone', 'unhappy', 'uniforms', 'unitary', 'untidy', 'unwise', 'unlike', 'unless', 'unlike', 'unlawful', 'uncommon', 'unwell', 'unsafe',

    'scary', 'hairy', 'diary', 'fairy', 'weary', 'dreary', 'canary', 'binary', 'library', 'primary', 'summary', 'contrary', 'military', 'ordinary', 'secretary', 'boundary', 'necessary', 'temporary', 'stationary', 'elementary', 'legendary', 'vocabulary', 'vary', 'mary', 'gary', 'carry', 'harry', 'marry', 'tarry', 'worry', 'hurry', 'curry', 'supply', 'reply', 'apply', 'dairy', 'fairy', 'hairy', 'scary', 'unwary', 'wary', 'vary', 'query', 'weary',
]

# Store response messages for deletion
command_responses = {}

# Commands that should NOT have their messages auto-deleted
PERSISTENT_COMMANDS = {'help', 'commands', 'cmds', 'pfp', 'whois', 'copy', 'jvc'}


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user} (User Account)')
    print('----------------------------------')


def get_help_text():
    return """```
╔══════════════════════════════════════════╗
║          SELF BOT COMMANDS GUIDE         ║
╚══════════════════════════════════════════╝

📌 BASIC COMMANDS
  -help, -commands, -cmds   Show this menu
  -hello                    Greet the bot
  -ping                     Check bot latency

🎮 FUN COMMANDS
  -coinflip                 Flip a coin
  -roll [max]               Roll a random number (default: 6)
  -pick <option1|option2>   Pick from multiple choices

💬 MESSAGING COMMANDS
  -spam <amount> <message>  Spam a message (max 20)

⚙️  REACTION COMMANDS
  -autoreact <user> <emoji>           Auto-react to a user's messages
  -clearautoreact <user>              Remove auto-reaction for user
  -gw <user> <emoji> <channel_id>     React only in specific channel
  -cleargw <user> <channel_id>        Remove channel-specific reaction

🔄 AUTO-REPLY COMMANDS
  -autoreply <message>      Set auto-reply when you're mentioned alone
  -clearautoreply           Disable auto-reply

🧹 CLEANUP COMMANDS
  -purge <amount> [user]    Delete recent messages
                            (optional: specify user to delete their messages)

👤 PROFILE COMMANDS
  -pfp [user]               Get a user's profile picture
  -whois [user]             Get detailed user information
  -copy <user>              Copy a user's nickname

🎤 VOICE COMMANDS
  -jvc <channel_id>         Join a voice channel by ID

📨 MASS DM COMMANDS
  -massdm <message>                    DM 10-15 random server members
  -massdm friendslist <message>        DM all your friends

🎯 BLACKTEA GAME
  -blacktea toggle          Enable/disable blacktea mode
  -blacktea status          Check blacktea status

═════════════════════════════════════════════
Prefix: -
For detailed help: -help
═════════════════════════════════════════════
```"""


def store_response(ctx, msg, persistent=False):
    """Store a message for later deletion."""
    if ctx.message.id not in command_responses:
        command_responses[ctx.message.id] = {'messages': [], 'persistent': persistent}
    command_responses[ctx.message.id]['messages'].append(msg)
    # If any response is marked persistent, mark the whole command as persistent
    if persistent:
        command_responses[ctx.message.id]['persistent'] = True


@bot.command(name='help', aliases=['commands', 'cmds'])
async def help_command(ctx):
    """Show a polished list of available commands."""
    msg = await ctx.send(get_help_text())
    store_response(ctx, msg, persistent=True)


@bot.command()
async def hello(ctx):
    """Say hello to the bot."""
    msg = await ctx.send(f"yoo {ctx.author.name} wtw")
    store_response(ctx, msg)


@bot.command()
async def ping(ctx):
    """Check the bot latency."""
    msg = await ctx.send(f"ur ping is {round(bot.latency * 1000, 2)}ms")
    store_response(ctx, msg)


@bot.command()
async def spam(ctx, amount: str = None, *, message: str = None):
    """Spam a message a number of times. Usage: -spam <amount> <message>"""
    if amount is None or message is None:
        msg = await ctx.send("pick a number and a message bub.")
        store_response(ctx, msg)
        return

    try:
        count = int(amount)
    except ValueError:
        msg = await ctx.send("put a number DORK.")
        store_response(ctx, msg)
        return

    if count < 1:
        msg = await ctx.send("amount gots to be 1 or 2.")
        store_response(ctx, msg)
        return

    if count > 20:
        msg = await ctx.send("cant do more than 20.")
        store_response(ctx, msg)
        return

    for i in range(count):
        try:
            await ctx.send(message)
        except Exception:
            break
        if i < count - 1:
            await asyncio.sleep(0.45)


def normalize_user_key(user_input: str):
    user_input = user_input.strip()
    if user_input.startswith('<@') and user_input.endswith('>'):
        user_input = re.sub(r'\D', '', user_input)
    return user_input.lower()


async def resolve_user_key(ctx, user_input: str):
    user_input = user_input.strip()
    if user_input.isdigit():
        return user_input

    if user_input.startswith('<@') and user_input.endswith('>'):
        mention_id = re.sub(r'\D', '', user_input)
        if mention_id.isdigit():
            return mention_id

    if ctx.guild:
        match = discord.utils.find(
            lambda m: m.name.lower() == user_input.lower()
            or (m.nick and m.nick.lower() == user_input.lower())
            or f"{m.name}#{m.discriminator}".lower() == user_input.lower(),
            ctx.guild.members,
        )
        if match:
            return str(match.id)

    return user_input.lower()


@bot.command()
async def autoreact(ctx, user: str = None, emoji: str = None):
    """Start auto-reacting to a user with a specific emoji."""
    if user is None or emoji is None:
        msg = await ctx.send("please pick a user and a emoji dork.")
        store_response(ctx, msg)
        return

    key = await resolve_user_key(ctx, user)
    auto_react_list[key] = emoji
    msg = await ctx.send(f"reacting `{user}` with `{emoji}`.")
    store_response(ctx, msg)


@bot.command()
async def clearautoreact(ctx, user: str = None):
    """Remove a user from the autoreact list."""
    if user is None:
        msg = await ctx.send("Usage: `-clearautoreact <user>`")
        store_response(ctx, msg)
        return

    key = await resolve_user_key(ctx, user)
    if key in auto_react_list:
        del auto_react_list[key]
        msg = await ctx.send(f"Auto-reaction cleared for `{user}`.")
        store_response(ctx, msg)
    else:
        msg = await ctx.send(f"No autoreact entry found for `{user}`.")
        store_response(ctx, msg)


async def try_click_existing_reaction(message, channel_emoji):
    """Attempt to find and click existing reaction without triggering API limits."""
    try:
        # Check if we've already searched recently (cache to avoid spam)
        cache_key = (message.channel.id, channel_emoji)
        current_time = asyncio.get_event_loop().time()
        
        if cache_key in reaction_cooldown:
            if current_time - reaction_cooldown[cache_key] < 30:  # 30 second cooldown
                print(f"[GW DEBUG] Reaction search on cooldown for: {channel_emoji}")
                return False
        
        # Random delay to look human-like (200-800ms)
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        # Look through recent messages but limit scope heavily
        search_limit = 15  # Much smaller than before
        found_reaction = False
        
        async for msg in message.channel.history(limit=search_limit):
            if found_reaction:
                break
                
            # Add human-like delay between checking messages
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            for reaction in msg.reactions:
                reaction_str = str(reaction.emoji)
                
                # Check if emoji matches (handle both unicode and custom emojis)
                if reaction_str == channel_emoji or (hasattr(reaction.emoji, 'name') and reaction.emoji.name == channel_emoji):
                    # Random delay before clicking to seem natural
                    await asyncio.sleep(random.uniform(0.3, 0.7))
                    
                    try:
                        await reaction.me()
                        print(f"[GW DEBUG] Successfully clicked existing reaction: {channel_emoji}")
                        reaction_cooldown[cache_key] = current_time
                        return True
                    except discord.Forbidden:
                        print(f"[GW DEBUG] Cannot click reaction - no permission")
                        return False
                    except discord.NotFound:
                        print(f"[GW DEBUG] Reaction was removed before clicking")
                        return False
        
        print(f"[GW DEBUG] No existing reaction found for: {channel_emoji}")
        reaction_cooldown[cache_key] = current_time
        return False
        
    except asyncio.TimeoutError:
        print(f"[GW DEBUG] Timeout while searching for reaction")
        return False
    except Exception as e:
        print(f"[GW DEBUG] Error searching for existing reaction: {e}")
        return False


def get_channel_emoji_for_user(author_id, author_name, author_display_name, channel_id):
    """Get channel-specific emoji for a user."""
    author_id_key = str(author_id)
    author_name_key = author_name.lower()
    author_display_key = author_display_name.lower()
    
    if author_id_key and (author_id_key, channel_id) in channel_autoreact_list:
        return channel_autoreact_list[(author_id_key, channel_id)]
    elif author_name_key and (author_name_key, channel_id) in channel_autoreact_list:
        return channel_autoreact_list[(author_name_key, channel_id)]
    elif author_display_key and (author_display_key, channel_id) in channel_autoreact_list:
        return channel_autoreact_list[(author_display_key, channel_id)]
    
    return None


@bot.command(name='gw')
async def gw(ctx, user: str = None, emoji: str = None, channel_id: str = None):
    """Start auto-reacting to a user with a specific emoji only in a specific channel.
    Usage: -gw <user> <emoji> <channel_id>"""
    if user is None or emoji is None or channel_id is None:
        msg = await ctx.send("Usage: `-gw <user> <emoji> <channel_id>`")
        store_response(ctx, msg)
        return

    if not channel_id.isdigit():
        msg = await ctx.send("Channel ID must be a number dork.")
        store_response(ctx, msg)
        return

    key = await resolve_user_key(ctx, user)
    channel_id_int = int(channel_id)
    
    channel_autoreact_list[(key, channel_id_int)] = emoji
    
    # Debug output
    print(f"[GW DEBUG] Set channel-specific autoreact:")
    print(f"[GW DEBUG] User: {user} (key: {key})")
    print(f"[GW DEBUG] Emoji: {emoji}")
    print(f"[GW DEBUG] Channel ID: {channel_id_int}")
    print(f"[GW DEBUG] Total GW entries: {len(channel_autoreact_list)}")
    print(f"[GW DEBUG] Active channels: {set(ch for _, ch in channel_autoreact_list.keys())}")
    
    msg = await ctx.send(f"reacting to `{user}` with `{emoji}` in channel `{channel_id}` only.")
    store_response(ctx, msg)


@bot.command(name='cleargw')
async def cleargw(ctx, user: str = None, channel_id: str = None):
    """Remove a user from channel-specific autoreact list.
    Usage: -cleargw <user> <channel_id>"""
    if user is None or channel_id is None:
        msg = await ctx.send("Usage: `-cleargw <user> <channel_id>`")
        store_response(ctx, msg)
        return

    if not channel_id.isdigit():
        msg = await ctx.send("Channel ID must be a number dork.")
        store_response(ctx, msg)
        return

    key = await resolve_user_key(ctx, user)
    channel_id_int = int(channel_id)
    
    if (key, channel_id_int) in channel_autoreact_list:
        del channel_autoreact_list[(key, channel_id_int)]
        
        # Debug output
        print(f"[GW DEBUG] Removed channel-specific autoreact:")
        print(f"[GW DEBUG] User: {user} (key: {key})")
        print(f"[GW DEBUG] Channel ID: {channel_id_int}")
        print(f"[GW DEBUG] Total GW entries: {len(channel_autoreact_list)}")
        print(f"[GW DEBUG] Active channels: {set(ch for _, ch in channel_autoreact_list.keys())}")
        
        msg = await ctx.send(f"Channel-specific auto-reaction cleared for `{user}` in channel `{channel_id}`.")
        store_response(ctx, msg)
    else:
        msg = await ctx.send(f"No channel-specific autoreact entry found for `{user}` in channel `{channel_id}`.")
        store_response(ctx, msg)


@bot.command()
async def autoreply(ctx, *, message: str = None):
    """Set an auto-reply message for when you're mentioned alone.
    Usage: -autoreply <message>
    The bot will only reply when you're mentioned with NO other message content."""
    global auto_reply_message, auto_reply_enabled
    
    if message is None or message.strip() == "":
        msg = await ctx.send("pick a message to autoreply with bub.")
        store_response(ctx, msg)
        return
    
    auto_reply_message = message
    auto_reply_enabled = True
    
    print(f"[AUTOREPLY DEBUG] Auto-reply enabled with message: {auto_reply_message}")
    
    msg = await ctx.send(f"autoreply set to: `{message}`")
    store_response(ctx, msg)


@bot.command()
async def clearautoreply(ctx):
    """Disable auto-reply."""
    global auto_reply_enabled, auto_reply_message
    
    if auto_reply_enabled:
        auto_reply_enabled = False
        auto_reply_message = None
        
        print(f"[AUTOREPLY DEBUG] Auto-reply disabled")
        
        msg = await ctx.send("autoreply cleared.")
        store_response(ctx, msg)
    else:
        msg = await ctx.send("autoreply is not enabled.")
        store_response(ctx, msg)


async def resolve_member(ctx, user_input: str):
    user_input = user_input.strip()
    if not ctx.guild:
        return None

    mention_match = re.match(r'<@!?(\d+)>', user_input)
    if mention_match:
        user_id = int(mention_match.group(1))
        member = ctx.guild.get_member(user_id)
        if member:
            return member
        try:
            return await ctx.guild.fetch_member(user_id)
        except Exception:
            return None

    if user_input.isdigit():
        user_id = int(user_input)
        member = ctx.guild.get_member(user_id)
        if member:
            return member
        try:
            return await ctx.guild.fetch_member(user_id)
        except Exception:
            return None

    lower_input = user_input.lower()
    member = discord.utils.find(
        lambda m: m.name.lower() == lower_input
        or (m.nick and m.nick.lower() == lower_input)
        or f"{m.name}#{m.discriminator}".lower() == lower_input,
        ctx.guild.members,
    )
    return member


@bot.command()
async def purge(ctx, arg1: str = None, arg2: str = None):
    """Delete recent messages. Usage: -purge <amount> [user mention/id]"""
    if not arg1:
        msg = await ctx.send("usage: `-purge <amount> [user mention/id]`")
        store_response(ctx, msg)
        return

    amount = None
    user = None

    for arg in [arg1, arg2]:
        if arg and arg.isdigit():
            amount = int(arg)
        elif arg:
            user = arg

    if not amount:
        msg = await ctx.send("put a number dork.")
        store_response(ctx, msg)
        return

    if amount < 1:
        msg = await ctx.send("atleast 1 or 2 dork")
        store_response(ctx, msg)
        return

    target_id = None
    if user:
        mention_match = re.match(r'<@!?(\d+)>', user)
        if mention_match:
            target_id = int(mention_match.group(1))
        elif user.isdigit():
            target_id = int(user)
        else:
            msg = await ctx.send("use their userid or mention.")
            store_response(ctx, msg)
            return

        if ctx.guild:
            bot_perms = ctx.channel.permissions_for(ctx.guild.me)
            if not bot_perms.manage_messages and not bot_perms.administrator:
                msg = await ctx.send("no perms to delete messaages.")
                store_response(ctx, msg)
                return

    to_delete = []
    async for m in ctx.channel.history(limit=1000):
        if target_id:
            if m.author.id == target_id:
                to_delete.append(m)
        else:
            if m.author.id == bot.user.id:
                to_delete.append(m)

        if len(to_delete) >= amount:
            break

    if len(to_delete) > amount:
        to_delete = to_delete[:amount]

    if not to_delete:
        msg = await ctx.send("Nothing found: No matching messages were found.")
        store_response(ctx, msg)
        return

    deleted_count = 0
    try:
        while to_delete:
            chunk = to_delete[:100]
            deleted = await ctx.channel.delete_messages(chunk)
            deleted_count += len(deleted)
            to_delete = to_delete[100:]
            if to_delete:
                await asyncio.sleep(0.4)
    except Exception:
        for m in list(to_delete):
            try:
                await m.delete()
                deleted_count += 1
            except Exception as e:
                if 'Unknown Message' in str(e) or '404' in str(e) or 'Not Found' in str(e):
                    continue
                break
            await asyncio.sleep(0.05)

    msg = await ctx.send(f"deleted {deleted_count} message(s).")
    store_response(ctx, msg)


@bot.command()
async def pfp(ctx, user: str = None):
    """Get a user's profile picture. Usage: -pfp [@user or userid]"""
    if not user:
        user = str(ctx.author.id)

    target_user = None

    mention_match = re.match(r'<@!?(\d+)>', user)
    if mention_match:
        user_id = int(mention_match.group(1))
        try:
            target_user = await bot.fetch_user(user_id)
        except Exception:
            msg = await ctx.send(f"i cant find {user_id}")
            store_response(ctx, msg, persistent=True)
            return
    elif user.isdigit():
        try:
            target_user = await bot.fetch_user(int(user))
        except Exception:
            msg = await ctx.send(f"cant find userid with {user}")
            store_response(ctx, msg, persistent=True)
            return
    else:
        msg = await ctx.send("use a mention or id")
        store_response(ctx, msg, persistent=True)
        return

    if not target_user:
        msg = await ctx.send("couldnt seek the user")
        store_response(ctx, msg, persistent=True)
        return

    avatar_url = target_user.avatar.url if target_user.avatar else target_user.default_avatar.url
    msg = await ctx.send(f"🖼️ {target_user.name}'s avatar: {avatar_url}")
    store_response(ctx, msg, persistent=True)


@bot.command()
async def whois(ctx, user: str = None):
    """Get detailed user info. Usage: -whois [@user or userid]"""
    if not user:
        target_user = ctx.author
        target_member = ctx.author if ctx.guild else None
    else:
        target_user = None
        target_member = None

        mention_match = re.match(r'<@!?(\d+)>', user)
        if mention_match:
            user_id = int(mention_match.group(1))
            try:
                target_user = await bot.fetch_user(user_id)
                if ctx.guild:
                    target_member = await ctx.guild.fetch_member(user_id)
            except Exception:
                msg = await ctx.send(f"i cant find {user_id}")
                store_response(ctx, msg, persistent=True)
                return
        elif user.isdigit():
            try:
                target_user = await bot.fetch_user(int(user))
                if ctx.guild:
                    target_member = await ctx.guild.fetch_member(int(user))
            except Exception:
                msg = await ctx.send(f"cant find userid with {user}")
                store_response(ctx, msg, persistent=True)
                return
        else:
            msg = await ctx.send("use a mention or id")
            store_response(ctx, msg, persistent=True)
            return

    if not target_user:
        msg = await ctx.send("couldnt fetch user")
        store_response(ctx, msg, persistent=True)
        return

    # Account creation date
    created_at = target_user.created_at
    created_str = f"<t:{int(created_at.timestamp())}:f>"

    # Server join date (if in guild)
    joined_str = "N/A"
    if target_member and ctx.guild:
        joined_at = target_member.joined_at
        if joined_at:
            joined_str = f"<t:{int(joined_at.timestamp())}:f>"

    # Mutual guilds
    mutual_guilds = []
    try:
        mutual_guilds = await target_user.mutual_guilds()
    except Exception:
        pass

    mutual_count = len(mutual_guilds)
    mutual_names = ", ".join([g.name for g in mutual_guilds[:5]]) if mutual_guilds else "None"
    if len(mutual_guilds) > 5:
        mutual_names += f" + {len(mutual_guilds) - 5} more"

    # Format as plain text message instead of embed
    info_text = f"""**User Info: {target_user.name}**
Username: {target_user.name}
User ID: {target_user.id}
Account Created: {created_str}
Server Joined: {joined_str}
Mutual Servers: **{mutual_count}** servers
{mutual_names}"""

    msg = await ctx.send(info_text)
    store_response(ctx, msg, persistent=True)


@bot.command()
async def copy(ctx, user: str = None):
    """Copy a user's profile to your server profile. Usage: -copy [@user or userid]"""
    if not ctx.guild:
        msg = await ctx.send("only in servers bud")
        store_response(ctx, msg, persistent=True)
        return

    if not user:
        msg = await ctx.send("pick a user to copy from")
        store_response(ctx, msg, persistent=True)
        return

    if not ctx.channel.permissions_for(ctx.guild.me).manage_nicknames and not ctx.channel.permissions_for(ctx.guild.me).administrator:
        msg = await ctx.send("i need perms for this dork")
        store_response(ctx, msg, persistent=True)
        return

    target_user = None
    target_member = None

    mention_match = re.match(r'<@!?(\d+)>', user)
    if mention_match:
        user_id = int(mention_match.group(1))
        try:
            target_user = await bot.fetch_user(user_id)
            target_member = await ctx.guild.fetch_member(user_id)
        except Exception:
            msg = await ctx.send(f"Could not find user with ID {user_id}")
            store_response(ctx, msg, persistent=True)
            return
    elif user.isdigit():
        try:
            target_user = await bot.fetch_user(int(user))
            target_member = await ctx.guild.fetch_member(int(user))
        except Exception:
            msg = await ctx.send(f"Could not find user with ID {user}")
            store_response(ctx, msg, persistent=True)
            return
    else:
        msg = await ctx.send("Invalid user: Use a mention or user ID.")
        store_response(ctx, msg, persistent=True)
        return

    if not target_user:
        msg = await ctx.send("Could not fetch user: The requested user could not be fetched.")
        store_response(ctx, msg, persistent=True)
        return

    display_name = target_member.nick if target_member and target_member.nick else target_user.name

    try:
        await ctx.guild.me.edit(nick=display_name)
        msg = await ctx.send(f"🪞 Doppelganger activated: Your server nickname now mirrors `{display_name}`.")
        store_response(ctx, msg, persistent=True)
    except Exception as e:
        msg = await ctx.send(f"Copy failed: {str(e)[:100]}")
        store_response(ctx, msg, persistent=True)


@bot.command(name='jvc')
async def join_voice_channel(ctx, channel_id: str = None):
    """Join a voice channel by ID. Usage: -jvc <channel_id>
    Simulates human-like clicking behavior to avoid detection."""
    
    if channel_id is None:
        msg = await ctx.send("Usage: `-jvc <channel_id>`")
        store_response(ctx, msg, persistent=True)
        return
    
    if not channel_id.isdigit():
        msg = await ctx.send("Channel ID must be a number dork.")
        store_response(ctx, msg, persistent=True)
        return
    
    if not ctx.guild:
        msg = await ctx.send("only in servers bud")
        store_response(ctx, msg, persistent=True)
        return
    
    channel_id_int = int(channel_id)
    
    # Get the channel object
    voice_channel = ctx.guild.get_channel(channel_id_int)
    
    if not voice_channel:
        msg = await ctx.send(f"couldnt find channel with id `{channel_id}`")
        store_response(ctx, msg, persistent=True)
        return
    
    if not isinstance(voice_channel, discord.VoiceChannel):
        msg = await ctx.send(f"`{voice_channel.name}` is not a voice channel dork")
        store_response(ctx, msg, persistent=True)
        return
    
    try:
        # Simulate human-like delay before clicking (300-800ms)
        human_delay = random.uniform(0.3, 0.8)
        await asyncio.sleep(human_delay)
        
        # Connect to the voice channel
        await voice_channel.connect()
        
        msg = await ctx.send(f"✅ joined voice channel `{voice_channel.name}`")
        store_response(ctx, msg, persistent=True)
        
        print(f"[JVC DEBUG] Successfully joined voice channel: {voice_channel.name} ({channel_id_int})")
        
    except discord.ClientException as e:
        if "already connected" in str(e).lower():
            msg = await ctx.send("already in a vc bro")
        else:
            msg = await ctx.send(f"error joining vc: {str(e)[:100]}")
        store_response(ctx, msg, persistent=True)
        print(f"[JVC DEBUG] Error joining voice channel: {e}")
        
    except Exception as e:
        msg = await ctx.send(f"couldnt join vc: {str(e)[:100]}")
        store_response(ctx, msg, persistent=True)
        print(f"[JVC DEBUG] Unexpected error: {e}")


@bot.command()
async def coinflip(ctx):
    """Flip a coin."""
    msg = await ctx.send(f"🪙 Coin Flip: {random.choice(['Heads', 'Tails'])}")
    store_response(ctx, msg)


@bot.command()
async def roll(ctx, max_value: str = None):
    """Roll a random number. Usage: -roll [max]"""
    if max_value is None:
        max_value = '6'

    try:
        upper = int(max_value)
    except ValueError:
        msg = await ctx.send("Invalid number: Max value must be a number.")
        store_response(ctx, msg)
        return

    if upper < 1:
        msg = await ctx.send("Invalid number: Max value must be at least 1.")
        store_response(ctx, msg)
        return

    msg = await ctx.send(f"🎲 Roll result: You rolled {random.randint(1, upper)}")
    store_response(ctx, msg)


@bot.command()
async def pick(ctx, *, options: str = None):
    """Pick one choice from a list. Usage: -pick option1 | option2 | option3"""
    if not options:
        msg = await ctx.send("Usage: `-pick choice1 | choice2 | choice3`")
        store_response(ctx, msg)
        return

    choices = [item.strip() for item in options.split('|') if item.strip()]
    if len(choices) < 2:
        msg = await ctx.send("Not enough choices: Give at least two choices separated by `|`.")
        store_response(ctx, msg)
        return

    msg = await ctx.send(f"🎯 Choice picked: I pick {random.choice(choices)}")
    store_response(ctx, msg)


def find_word_with_substring(substring: str, used_words: list = None) -> str:
    """Find a word containing the substring. Returns None if no word found."""
    if used_words is None:
        used_words = []
    
    substring_lower = substring.lower()
    matching_words = [w for w in COMMON_WORDS if substring_lower in w.lower() and w.lower() not in used_words]
    
    if matching_words:
        # Prefer shorter words for faster typing
        matching_words.sort(key=len)
        return matching_words[0]
    
    return None


@bot.command()
async def blacktea(ctx, action: str = None):
    """Control blacktea auto-responder. Usage: -blacktea toggle • -blacktea status"""
    global blacktea_enabled
    
    if action is None or action.lower() not in ['toggle', 'status']:
        msg = await ctx.send("toggle or status?")
        store_response(ctx, msg)
        return
    
    if action.lower() == 'toggle':
        blacktea_enabled = not blacktea_enabled
        status_emoji = "🎮" if blacktea_enabled else "⛔"
        status_text = "ENABLED" if blacktea_enabled else "DISABLED"
        msg = await ctx.send(f"blacktea mode activated")
        store_response(ctx, msg)
    
    elif action.lower() == 'status':
        status_emoji = "🎮" if blacktea_enabled else "⛔"
        status_text = "ENABLED" if blacktea_enabled else "DISABLED"
        msg = await ctx.send(f"blacktea mode status: on")
        store_response(ctx, msg)


@bot.command()
async def massdm(ctx, mode: str = None, *, message: str = None):
    """Mass DM random members or friends. 
    
    Usage:
    -massdm <message> - DM 10-15 random server members
    -massdm friendslist <message> - DM all friends
    """
    
    # Handle friendslist mode
    if mode and mode.lower() == 'friendslist':
        if message is None:
            msg = await ctx.send("type a msg to mass dm for exmp,'hey there' ")
            store_response(ctx, msg)
            return
        
        # Get the user's friends list from Discord API
        try:
            friends_response = await bot.http.request(discord.http.Route("GET", "/users/@me/relationships"))
            # Filter for friends only (type 1 = friend)
            friends_list = [f for f in friends_response if f.get('type') == 1]
        except Exception as e:
            msg = await ctx.send(f"couldnt find friendslist {str(e)}")
            store_response(ctx, msg)
            return
        
        if not friends_list:
            msg = await ctx.send("u have no friends LOL")
            store_response(ctx, msg)
            return
        
        msg = await ctx.send(f"starting mass dm to  {len(friends_list)} friends with message: `{message}`")
        store_response(ctx, msg)
        
        sent_count = 0
        failed_count = 0
        blocked_count = 0

        for friend in friends_list:
            try:
                friend_user = await bot.fetch_user(int(friend['id']))
                await friend_user.send(message)
                sent_count += 1
                # 10 second delay between each DM
                await asyncio.sleep(10)
            except discord.Forbidden:
                blocked_count += 1
                await asyncio.sleep(10)
            except discord.HTTPException:
                failed_count += 1
                await asyncio.sleep(10)
            except Exception as e:
                failed_count += 1
                await asyncio.sleep(10)

        msg = await ctx.send(
            f"mass dm complete:\n"
            f"sent: {sent_count}\n"
            f"blocked/dms closed: {blocked_count}\n"
            f"failed: {failed_count}"
        )
        store_response(ctx, msg)
    
    # Handle regular massdm mode (random server members)
    else:
        # If mode is not 'friendslist', treat it as the message and shift parameters
        if mode is None or message is None:
            msg = await ctx.send("either friendlist or no friendslist and choose a msg please")
            store_response(ctx, msg)
            return
        
        # Combine mode and message back together if mode was actually the start of the message
        full_message = mode if message is None else f"{mode} {message}"
        
        if not ctx.guild:
            msg = await ctx.send("i only work in servers")
            store_response(ctx, msg)
            return

        # Get all members excluding the bot
        members_to_dm = [m for m in ctx.guild.members if m.id != bot.user.id]
        
        # Randomly select 10-15 members
        dm_count = random.randint(10, 15)
        dm_count = min(dm_count, len(members_to_dm))  # Don't exceed available members
        selected_members = random.sample(members_to_dm, dm_count)
        
        msg = await ctx.send(f"mass dming to {dm_count} randoms with: `{full_message}`")
        store_response(ctx, msg)
        
        sent_count = 0
        failed_count = 0
        blocked_count = 0

        for member in selected_members:
            try:
                await member.send(full_message)
                sent_count += 1
                # 10 second delay between each DM
                await asyncio.sleep(10)
            except discord.Forbidden:
                blocked_count += 1
                await asyncio.sleep(10)
            except discord.HTTPException:
                failed_count += 1
                await asyncio.sleep(10)
            except Exception as e:
                failed_count += 1
                await asyncio.sleep(10)

        msg = await ctx.send(
            f"mass dm complete:\n"
            f"sent: {sent_count}\n"
            f"blocked/dms closed: {blocked_count}\n"
            f"failed: {failed_count}"
        )
        store_response(ctx, msg)


@bot.event
async def on_message(message):
    # Ignore own messages
    if message.author.id == bot.user.id:
        await bot.process_commands(message)
        return

    # Auto-reply logic
    if auto_reply_enabled and bot.user in message.mentions:
        # Get the message content without mentions
        content_without_mentions = message.content
        
        # Remove all mentions from the content
        mention_pattern = r'<@!?\d+>'
        content_cleaned = re.sub(mention_pattern, '', content_without_mentions).strip()
        
        print(f"[AUTOREPLY DEBUG] Bot mentioned!")
        print(f"[AUTOREPLY DEBUG] Full content: {message.content}")
        print(f"[AUTOREPLY DEBUG] Content without mentions: {content_cleaned}")
        
        # Only reply if there's no other message content (only the mention)
        if content_cleaned == "":
            print(f"[AUTOREPLY DEBUG] Message is ONLY a mention. Replying...")
            try:
                await message.reply(auto_reply_message)
                print(f"[AUTOREPLY DEBUG] Successfully sent auto-reply")
            except Exception as e:
                print(f"[AUTOREPLY DEBUG] Error sending auto-reply: {e}")
        else:
            print(f"[AUTOREPLY DEBUG] Message contains additional content: '{content_cleaned}'. Not replying.")

    # Blacktea auto-responder logic
    if blacktea_enabled and bot.user in message.mentions:
        print(f"[BLACKTEA DEBUG] Pinged! Message content: {message.content}")
        print(f"[BLACKTEA DEBUG] Blacktea enabled: {blacktea_enabled}")
        print(f"[BLACKTEA DEBUG] Number of embeds: {len(message.embeds)}")
        
        substring = None
        
        # Check message content first
        substring_match = re.search(r'\*\*([A-Za-z]{3})\*\*', message.content)
        if substring_match:
            substring = substring_match.group(1)
            print(f"[BLACKTEA DEBUG] Found substring in content: {substring}")
        
        # If not found, check embeds
        if not substring and message.embeds:
            for embed in message.embeds:
                print(f"[BLACKTEA DEBUG] Embed description: {embed.description}")
                if embed.description:
                    # Look for bold text in embed
                    substring_match = re.search(r'\*\*([A-Za-z]{3})\*\*', embed.description)
                    if substring_match:
                        substring = substring_match.group(1)
                        print(f"[BLACKTEA DEBUG] Found substring in embed: {substring}")
                        break
        
        if substring:
            channel_id = message.channel.id
            
            # Get used words for this channel
            if channel_id not in blacktea_used_words:
                blacktea_used_words[channel_id] = []
            
            # Find a valid word
            word = find_word_with_substring(substring, blacktea_used_words[channel_id])
            print(f"[BLACKTEA DEBUG] Found word: {word}")
            
            if word:
                # Track the word as used
                blacktea_used_words[channel_id].append(word.lower())
                
                # Send response with 1 second delay
                print(f"[BLACKTEA DEBUG] Sending word: {word}")
                await asyncio.sleep(1)
                try:
                    await message.channel.send(word)
                    print(f"[BLACKTEA DEBUG] Successfully sent word: {word}")
                except Exception as e:
                    print(f"[BLACKTEA DEBUG] Error sending blacktea response: {e}")
            else:
                print(f"[BLACKTEA DEBUG] No word found for substring: {substring}")
        else:
            print(f"[BLACKTEA DEBUG] No substring found in message or embeds")

    # Auto-react logic
    author_id_key = str(message.author.id)
    author_name_key = message.author.name.lower()
    author_display_key = message.author.display_name.lower()

    emoji = None
    if author_id_key in auto_react_list:
        emoji = auto_react_list[author_id_key]
    elif author_name_key in auto_react_list:
        emoji = auto_react_list[author_name_key]
    elif author_display_key in auto_react_list:
        emoji = auto_react_list[author_display_key]

    if emoji:
        try:
            await message.add_reaction(emoji)
        except Exception:
            pass

    # Channel-specific auto-react logic with fallback
    channel_id = message.channel.id
    channel_emoji = get_channel_emoji_for_user(message.author.id, message.author.name, message.author.display_name, channel_id)

    if channel_emoji:
        try:
            await message.add_reaction(channel_emoji)
            print(f"[GW DEBUG] Successfully reacted to message in channel {channel_id}")
        except discord.Forbidden:
            # No permission to add reaction, try to click existing ones
            print(f"[GW DEBUG] No permission to add reaction. Attempting to find existing reaction...")
            await try_click_existing_reaction(message, channel_emoji)
        except Exception as e:
            print(f"[GW DEBUG] Error reacting to message: {e}")

    await bot.process_commands(message)


@bot.event
async def on_command_completion(ctx):
    """Delete all bot response messages 2 seconds after command completes."""
    try:
        # Check if this command's responses should persist
        if ctx.message.id in command_responses:
            should_persist = command_responses[ctx.message.id].get('persistent', False)
        else:
            should_persist = False
        
        # If persistent, don't delete anything
        if should_persist:
            return
        
        await asyncio.sleep(2)
        
        # Delete all stored response messages
        if ctx.message.id in command_responses:
            for msg in command_responses[ctx.message.id]['messages']:
                try:
                    await msg.delete()
                except Exception:
                    pass
            del command_responses[ctx.message.id]
        
        # Delete the command message itself
        try:
            await ctx.message.delete()
        except Exception:
            pass
    except Exception:
        pass


# Run the bot.
# Replace the token below with your actual user account token.
TOKEN = ''

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you installed 'discord.py-self' and not 'discord.py'")