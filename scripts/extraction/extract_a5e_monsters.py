import json
import re
from pdfminer.high_level import extract_text


def extract() -> str:
    inner = extract_text('../../sources/a5e_srd_19.1_monsters_A-F.pdf')
    inner = re.sub(r'A5E System Reference Document', '', inner)
    inner = re.sub(r"""



""", ' ', inner)
    inner = re.sub(r"`", '', inner)
    inner = re.sub(r"–", "-", inner)
    return re.sub(r"\u25cf", '-', inner)


def clean(input_text: str) -> dict:
    monster_text = ""
    drop = True
    for line in input_text.split('\n'):
        if line == 'Aboleth':
            drop = False

        if not drop:
            monster_text += line + '\n'

    monsters = dict()
    monster = ""
    current = ""
    for line in monster_text.split('\n'):
        if re.match(r'^[A-Z ]+ CHALLENGE', line):
            if current != "":
                monsters[current] = monster
            current = re.match(r'^([A-Z ]+) CHALLENGE', line).group(1)
            monster = line + '\n'
        else:
            monster += line + '\n'

    monsters[current] = monster

    with open('../../sources/a5e_monsters.json', 'w', encoding='utf-8') as f:
        json.dump(monsters, f, indent=4, ensure_ascii=False)
    return monsters


regex = re.compile(r"^(?P<name>[\w ]+) CHALLENGE (?P<challenge_rating>[\d/]+) "
                   r"((?P<legendary>LEGENDARY) )?"
                   r"(?P<size>TINY|SMALL|MEDIUM|LARGE|HUGE|GARGANTUAN) "
                   r"(?P<type>ABERRATION|BEAST|CELESTIAL|CONSTRUCT|DRAGON|ELEMENTAL|FEY|FIEND|GIANT|HUMANOID|MONSTROSITY|OOZE|PLANT|UNDEAD) "
                   r"(\((?P<subtype>[\w, ]+)\) )?"
                   r"(?P<xp>[\d,]+) XP "
                   r"AC (?P<ac>\d+)( \((?P<ac_source>[\w, ]+)\))?( or 14 while unarmored|, 10 while prone|, 14 while prone)? "
                   r"HP (?P<hp>\d+) \((?P<hitdice>[\dd+ ]+); bloodied (?P<bloodied>\d+)\) "
                   r"Speed (?P<speed>\d+) ft\.(, burrow (?P<burrow>\d+) ft\.)?(, climb (?P<climb>\d+) ft\.)?(, fly (?P<fly>\d+) ft\.(?P<can_hover> \(hover\))?( \(maximum elevation (?P<max_elevation>10) feet\))?)?(, burrow (?P<burrow_2>\d+) ft\.)?(, swim (?P<swim>\d+) ft\.?)? "
                   r"STR DEX CON INT WIS CHA (?P<strength>\d+) ?\([+-]\d+\) ?(?P<dexterity>\d+) ?\([+-]\d+\) ?(?P<constitution>\d+) ?\([+-]\d+\) ?(?P<intelligence>\d+) ?\([+-]\d+\) ?(?P<wisdom>\d+) ?\([+-]\d+\) ?(?P<charisma>\d+) ?\([+-]\d+\) "
                   r"(Proficiency \+(?P<proficiency>\d+); Maneuver DC (?P<maneuver_dc>\d+) )?"
                   r"(?P<has_saving_throws>Saving Throws )?(Str \+(?P<saving_throw_str>\d+),? )?(Dex \+(?P<saving_throw_dex>\d+),? )?(Con \+(?P<saving_throw_con>\d+),? )?(Int [+-](?P<saving_throw_int>\d+),? )?(Wis(dom)? \+ ?(?P<saving_throw_wis>\d+),? )?(Cha \+(?P<saving_throw_cha>\d+),? )?"
                   r"(Skills (?P<skills>(\w+ \+\d+( \(\+1d[46]\))?, )*\w+ \+\d+( \(\+1d[46]\))?) |Skills Any one skill )?"
                   r"(Damage Vulnerabilities (?P<damage_vulnerabilities>[^A-Z]+) )?"
                   r"(Damage Resistances (?P<damage_resistances>[^A-Z]+) )?"
                   r"(Damage Immunities (?P<damage_immunities>[^A-Z]+) )?"
                   r"(Condition Immunities (?P<condition_immunities>[^A-Z]+) )?"
                   r"(?P<senses>Senses (blindsight (?P<blindsight>\d+) ft\.( \((?P<blind_beyond>blind beyond this radius)\))?, )?(darkvision (?P<darkvision>\d+) ft\., )?(tremorsense (?P<tremorsense>\d+) ft\.(?P<only_in_water> \(only detects vibrations in water\))?, )?(truesight (?P<truesight>\d+) ft\., )?[pP]assive Perception (?P<passive_perception>\d+) )?"
                   )

print(regex.pattern)


def structure_output(monsters: dict):
    structured_monsters = dict()
    for monster in monsters:
        if monster == "HORDE DEMON BAND" or monster == "LEMURE BAND":
            continue

        structured_monster = dict()
        flat_monster = re.sub(r'\n+', ' ', monsters[monster])
        matches = regex.match(flat_monster)
        if matches:
            structured_monster['name'] = matches.group('name')
            structured_monster['challenge_rating'] = matches.group('challenge_rating')
            if matches.group('legendary'):
                structured_monster['is_legendary'] = True
            structured_monster['size'] = matches.group('size')
            structured_monster['type'] = matches.group('type')
            if matches.group('subtype'):
                structured_monster['subtype'] = [matches.group('subtype')] if ',' not in matches.group('subtype') else matches.group('subtype').split(', ')
            structured_monster['xp'] = matches.group('xp')
            structured_monster['ac'] = matches.group('ac')
            if matches.group('ac_source'):
                structured_monster['ac_source'] = [matches.group('ac_source')] if ',' not in matches.group('ac_source') else matches.group('ac_source').split(', ')
            structured_monster['hp'] = matches.group('hp')
            structured_monster['hitdice'] = matches.group('hitdice')
            structured_monster['bloodied'] = matches.group('bloodied')
            structured_monster['speed'] = matches.group('speed')
            if matches.group('fly'):
                structured_monster['fly'] = matches.group('fly')
                if matches.group('can_hover'):
                    structured_monster['can_hover'] = True
                if matches.group('max_elevation'):
                    structured_monster['max_elevation'] = matches.group('max_elevation')
            if matches.group('swim'):
                structured_monster['swim'] = matches.group('swim')
            if matches.group('climb'):
                structured_monster['climb'] = matches.group('climb')
            if matches.group('burrow'):
                structured_monster['burrow'] = matches.group('burrow')
            if matches.group('burrow_2'):
                structured_monster['burrow'] = matches.group('burrow_2')
            structured_monster['strength'] = matches.group('strength')
            structured_monster['dexterity'] = matches.group('dexterity')
            structured_monster['constitution'] = matches.group('constitution')
            structured_monster['intelligence'] = matches.group('intelligence')
            structured_monster['wisdom'] = matches.group('wisdom')
            structured_monster['charisma'] = matches.group('charisma')
            if matches.group('proficiency'):
                structured_monster['proficiency'] = matches.group('proficiency')
            if matches.group('maneuver_dc'):
                structured_monster['maneuver_dc'] = matches.group('maneuver_dc')


            if matches.group('has_saving_throws'):
                matched_any = False
                if matches.group('saving_throw_str'):
                    structured_monster['saving_throw_str'] = matches.group('saving_throw_str')
                    matched_any = True
                if matches.group('saving_throw_dex'):
                    structured_monster['saving_throw_dex'] = matches.group('saving_throw_dex')
                    matched_any = True
                if matches.group('saving_throw_con'):
                    structured_monster['saving_throw_con'] = matches.group('saving_throw_con')
                    matched_any = True
                if matches.group('saving_throw_int'):
                    structured_monster['saving_throw_int'] = matches.group('saving_throw_int')
                    matched_any = True
                if matches.group('saving_throw_wis'):
                    structured_monster['saving_throw_wis'] = matches.group('saving_throw_wis')
                    matched_any = True
                if matches.group('saving_throw_cha'):
                    structured_monster['saving_throw_cha'] = matches.group('saving_throw_cha')
                    matched_any = True
                if not matched_any:
                    print(f"Error Saving Throws: {monster}\n{flat_monster}")

            if matches.group('skills'):
                values = matches.group('skills').split(', ')
                skills = dict()
                for value in values:
                    values = value.split(' ')
                    if len(values) == 3:
                        skill, modifier, die = values
                        skills[skill.lower()] = modifier.strip('+')
                        skills[skill.lower() + '_die'] = die
                    else:
                        skill, modifier = values
                        skills[skill.lower()] = modifier.strip('+')
                structured_monster['skills'] = skills

            if matches.group('senses'):
                senses = dict()
                if matches.group('blindsight'):
                    senses['blindsight'] = matches.group('blindsight')
                    if matches.group('blind_beyond'):
                        senses['blind_beyond_blindsight_range'] = True
                if matches.group('darkvision'):
                    senses['darkvision'] = matches.group('darkvision')
                if matches.group('tremorsense'):
                    senses['tremorsense'] = matches.group('tremorsense')
                    if matches.group('only_in_water'):
                        senses['tremorsense_only_in_water'] = True
                if matches.group('truesight'):
                    senses['truesight'] = matches.group('truesight')
                senses['passive_perception'] = matches.group('passive_perception')
            else:
                print(f"Error No Senses: {monster}\n{flat_monster}")

            if matches.group('damage_resistances'):
                structured_monster['damage_resistances'] = matches.group('damage_resistances')
        else:
            print(f"Error: {monster}\n{flat_monster}")

        structured_monsters[monster] = structured_monster

    with open('../../sources/a5e_monsters_structured.json', 'w', encoding='utf-8') as f:
        json.dump(structured_monsters, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    text = extract()
    monster_list = clean(text)
    structure_output(monster_list)
