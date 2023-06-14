from graphics import Canvas
import time
import random

WORLD_WIDTH = 40
WORLD_HEIGHT = 15
HEARTBEAT3 = 0.1
HEARTBEAT2 = 0.25
HEARTBEAT1 = 3
ALLOWED_TO_STEP_ON = ['☼', '♥', '.', 'B']
LIST_OF_ALLOWED_BUILDINGS = ['b', 'w', 'bed', 'beD', 'bEd', 'bED', 'Bed', 'BeD', 'BEd',
                             'BED', 'wall', 'walL', 'waLl', 'waLL', 'wAll', 'wAlL', 'wALl', 'wALL',
                             'Wall', 'WalL', 'WaLl', 'WaLL', 'WAll', 'WAlL', 'WALl', 'WALL']


def clear_console():
    for i in range(25):
        print()


def greeting_screen(c):
    print("Karel Fortress")
    print("This is dwarf: A")
    print("It ain't much but has an honest hat.")
    print()
    print("It is Dwarf Fortress like game, you are controlling a cursor ☼. You can point at a tree to order dwarf to chop it for wood, point at rock in order for it to be mined. You can biuld things on the ground represented by dots")
    print("Dwarf goes to heart representing food when it's hungry(fullness below 50) and goes to bed at 22 and wakes up at 6")
    print()
    print("Arrows control a cursor ☼, it starts at top left corner.")
    print("By pointing the cursor somewhere and pressing certain key you can order a dwarf to")
    print(" c - chop tree ♠, m - mine rock ■, b - build wooden wall ░ or bed B, g - just go for a walk")
    print("Additionally r - rescue(if dwarf is stuck), 1/2/3 - game speed")
    print("press enter to continue")
    key = ''
    while key != 'Enter':
        key = c.get_last_key_press()


def create_grid():
    grid = [['.' for _ in range(WORLD_WIDTH)] for _ in range(WORLD_HEIGHT)]
    return grid


def generate_mountain(grid):
    # I know it's kind of garbage, but I made it at beginning just to generate anything for testing purpose.
    beginning_y = int(WORLD_HEIGHT / 2)
    beginning_x = 0
    count_of_indentations_in_mountain_line = 0
    grid[beginning_y][beginning_x] = '■'
    fill_with_mountain_to_bottom(grid, beginning_y, beginning_x)
    for i in range(39):  # 39 is half of height + width, for now it is the longest route from 9,0 to 18,40
        if random.randint(0, 1) == 0 and beginning_x < WORLD_WIDTH - 5:
            # was supposed to be fancy random mountain generator
            # why WORLD_WIDTH - 5? Because for now we really don't want to generate anything outside of grid
            for j in range(4):
                beginning_x += 1
                grid[beginning_y][beginning_x] = '■'
                fill_with_mountain_to_bottom(grid, beginning_y, beginning_x)
        elif beginning_y < WORLD_HEIGHT - 1:
            if count_of_indentations_in_mountain_line < 5:
                # unfortunately for this scale 5 indentations are max
                beginning_y += 1
                count_of_indentations_in_mountain_line += 1
        else:
            return


def fill_with_mountain_to_bottom(grid, beginning_y, beginning_x):
    while beginning_y < WORLD_HEIGHT:
        grid[beginning_y][beginning_x] = '■'
        beginning_y += 1


def generate_trees(grid, num_trees):
    # trees must be integer like in a real world
    for i in range(num_trees):
        success = 0
        while success == 0:  # now I think about replacing this with "while grid[y][x] == '.':"
            # thou it's late night and I don't want to accidentally break it
            y = random.randint(0, WORLD_HEIGHT - 1)
            x = random.randint(0, WORLD_WIDTH - 1)
            if grid[y][x] == '.':
                grid[y][x] = '♠'
                success += 1


def add_dwarf(grid):
    while True:
        dwarf_y = random.randint(3, WORLD_HEIGHT - 4)
        dwarf_x = random.randint(3, WORLD_WIDTH - 4)
        # again, offset of three because don't want
        # food(which is honestly kind of dumb and generates regardless of anything)
        # nor dwarf flying outside the grid
        if grid[dwarf_y][dwarf_x] == '.':
            original_tenant = grid[dwarf_y][dwarf_x]
            grid[dwarf_y][dwarf_x] = 'A'
            return {'dwarf_y': dwarf_y, 'dwarf_x': dwarf_x,
                    'original_tenant': original_tenant,
                    'dwarf_hp': 30, 'dwarf_fullness': 100,
                    'dwarf_equipment': {'wood': 0, 'rock_chunks': 0, 'food': 0}}


def add_food(grid, dwarf, amount):
    food_y, food_x = dwarf['dwarf_y'], dwarf['dwarf_x']
    while True:
        food_y = food_y + random.randint(-1, 1)
        food_x = food_x + random.randint(-1, 1)
        if grid[food_y][food_x] == '.':
            grid[food_y][food_x] = '♥'
            return [food_y, food_x, amount]


def add_cursor(grid):
    cursor_y = 0
    cursor_x = 0
    original_tenant = grid[cursor_y][cursor_x]
    grid[cursor_y][cursor_x] = '☼'
    return {'cursor_y': cursor_y, 'cursor_x': cursor_x, 'original_tenant': original_tenant}


def display_grid(grid):
    for row in grid:
        for cell in row:
            print(cell, end=" ")  # to be honest "end=" "" is the only one thing
            # in this entire mess that I don't comprehend, it was suggested by GPT xD
        print()


def move_cursor(cursor, grid, key=''):
    cursor_y, cursor_x = cursor['cursor_y'], cursor['cursor_x']
    original_tenant = cursor['original_tenant']
    grid[cursor_y][cursor_x] = original_tenant
    if key == 'up' and cursor_y > 0:
        cursor_y -= 1
    elif key == 'left' and cursor_x > 0:
        cursor_x -= 1
    elif key == 'right' and cursor_x < (WORLD_WIDTH - 1):
        cursor_x += 1
    elif key == 'down' and cursor_y < (WORLD_HEIGHT - 1):
        cursor_y += 1
    original_tenant = grid[cursor_y][cursor_x]
    grid[cursor_y][cursor_x] = '☼'
    cursor['cursor_y'] = cursor_y
    cursor['cursor_x'] = cursor_x
    cursor['original_tenant'] = original_tenant


def create_goal(cursor, key, food, bed, is_it_night_or_day):
    cursor_y, cursor_x = cursor['cursor_y'], cursor['cursor_x']
    original_tenant = cursor['original_tenant']
    if key == 'm' and original_tenant == '■' and is_it_night_or_day == 'day':
        goal = 'mine'
        return {'goal': goal, 'goal_y': cursor_y, 'goal_x': cursor_x, 'goal_original_tenant': original_tenant}
        # this is the tricky part where target graphic
        # needs to be stored somewhere for later to be used in one specific place
    elif key == 'c' and original_tenant == '♠' and is_it_night_or_day == 'day':
        goal = 'chop'
        return {'goal': goal, 'goal_y': cursor_y, 'goal_x': cursor_x, 'goal_original_tenant': original_tenant}
    elif key == 'b' and original_tenant == '.' and is_it_night_or_day == 'day':
        goal = 'build'
        return {'goal': goal, 'goal_y': cursor_y, 'goal_x': cursor_x, 'goal_original_tenant': original_tenant}
    elif key == 'g' and original_tenant == '.' and is_it_night_or_day == 'day':
        goal = 'go'
        return {'goal': goal, 'goal_y': cursor_y, 'goal_x': cursor_x, 'goal_original_tenant': original_tenant}
    elif key == 'hungry':
        goal = 'eat'
        return {'goal': goal, 'goal_y': food[0], 'goal_x': food[1], 'goal_original_tenant': '♥'}
    elif key == 'sleepy':
        goal = 'sleep'
        if bed['bed_y'] == 0 and bed['bed_x'] == 0:
            return {'goal': goal, 'goal_y': bed['bed_y'], 'goal_x': bed['bed_x'], 'goal_original_tenant': '.'}
        return {'goal': goal, 'goal_y': bed['bed_y'], 'goal_x': bed['bed_x'], 'goal_original_tenant': 'B'}
    else:
        return 'none'  # magic of python I guess - variable "goal"
        # doesn't mind being mostly string but from time to time a dict


def action_of_dwarf(dwarf, grid, cursor, goal, food, speed, bed, c):
    move_dwarf(dwarf, grid, cursor, goal, speed, c)
    if dwarf['dwarf_y'] == goal['goal_y'] and dwarf['dwarf_x'] == goal['goal_x']:
        if goal['goal'] == 'chop':
            dwarf['original_tenant'] = '.'
            dwarf['dwarf_equipment']['wood'] += 15
        if goal['goal'] == 'mine':
            dwarf['original_tenant'] = '.'
            dwarf['dwarf_equipment']['rock_chunks'] += 10
        if goal['goal'] == 'build':
            desired_building = ''
            if dwarf['dwarf_equipment']['wood'] >= 5:
                print("What would you like to build?(options are: bed, wall)")
                key = ''
                input_building = ''
                while key != 'Enter':
                    key = c.get_last_key_press()
                    if key != 'Enter' and key != None:
                        input_building += str(key)
                while not (input_building in LIST_OF_ALLOWED_BUILDINGS):
                    print("Please enter a correct command")
                    print("What would you like to build?(options are: bed, wall)")
                    key = ''
                    input_building = ''
                    while key != 'Enter':
                        key = c.get_last_key_press()
                        if key != 'Enter' and key != None:
                            input_building += str(key)
                if input_building in ['w', 'wall', 'walL', 'waLl', 'waLL', 'wAll', 'wAlL', 'wALl', 'wALL',
                                      'Wall', 'WalL', 'WaLl', 'WaLL', 'WAll', 'WAlL', 'WALl', 'WALL']:
                    desired_building = 'wall'
                elif input_building in ['b', 'bed', 'beD', 'bEd', 'bED', 'Bed', 'BeD', 'BEd', 'BED']:
                    desired_building = 'bed'
                if desired_building == 'wall':
                    dwarf['original_tenant'] = '░'
                    dwarf['dwarf_equipment']['wood'] -= 5
                elif desired_building == 'bed':
                    dwarf['original_tenant'] = 'B'
                    bed['bed_y'] = goal['goal_y']
                    bed['bed_x'] = goal['goal_x']
                    dwarf['dwarf_equipment']['wood'] -= 5
                elif desired_building == '':
                    print("Please report this bug")
                    input("Press enter")
            else:
                print("Not enough wood, chop some by pointing at a tree ♠ and pressing 'c'")
                print("Press enter")
                key = ''
                while key != 'Enter':
                    key = c.get_last_key_press()

        if goal['goal'] == 'eat':
            food[2] -= 1
            dwarf['dwarf_fullness'] = 100
        # if goal['goal'] == 'sleep':


def move_dwarf(dwarf, grid, cursor, goal, speed, c):
    while dwarf['dwarf_y'] != goal['goal_y'] or dwarf['dwarf_x'] != goal['goal_x']:
        dwarf_y, dwarf_x = dwarf['dwarf_y'], dwarf['dwarf_x']
        previous_dwarf_y, previous_dwarf_x = dwarf_y, dwarf_x
        goal_y, goal_x = goal['goal_y'], goal['goal_x']
        original_tenant = dwarf['original_tenant']
        grid[dwarf_y][dwarf_x] = original_tenant
        if dwarf_y < goal_y and grid[dwarf_y + 1][dwarf_x] in ALLOWED_TO_STEP_ON and dwarf_y + 1 != WORLD_HEIGHT:
            dwarf_y += 1
        elif dwarf_y > goal_y and grid[dwarf_y - 1][dwarf_x] in ALLOWED_TO_STEP_ON and dwarf_y - 1 != -1:
            dwarf_y -= 1
        elif dwarf_x < goal_x and grid[dwarf_y][dwarf_x + 1] in ALLOWED_TO_STEP_ON and dwarf_x + 1 != WORLD_WIDTH:
            dwarf_x += 1
        elif dwarf_x > goal_x and grid[dwarf_y][dwarf_x - 1] in ALLOWED_TO_STEP_ON and dwarf_x - 1 != -1:
            dwarf_x -= 1
        while previous_dwarf_y == dwarf_y and previous_dwarf_x == dwarf_x:
            if dwarf_y == goal_y:
                if dwarf_x > goal_x:
                    if dwarf_y + 1 != WORLD_HEIGHT and dwarf_x - 1 != -1 and \
                            grid[dwarf_y + 1][dwarf_x - 1] in ALLOWED_TO_STEP_ON:
                        dwarf_y += 1
                        dwarf_x -= 1
                    elif dwarf_y - 1 != -1 and dwarf_x - 1 != -1 and \
                            grid[dwarf_y - 1][dwarf_x - 1] in ALLOWED_TO_STEP_ON:
                        dwarf_y -= 1
                        dwarf_x -= 1
                if dwarf_x < goal_x:
                    if dwarf_y + 1 != WORLD_HEIGHT and dwarf_x + 1 != WORLD_WIDTH and \
                            grid[dwarf_y + 1][dwarf_x + 1] in ALLOWED_TO_STEP_ON:
                        dwarf_y += 1
                        dwarf_x += 1
                    elif dwarf_y - 1 != -1 and dwarf_x + 1 != WORLD_WIDTH and \
                            grid[dwarf_y - 1][dwarf_x + 1] in ALLOWED_TO_STEP_ON:
                        dwarf_y -= 1
                        dwarf_x += 1
            if previous_dwarf_y == dwarf_y and previous_dwarf_x == dwarf_x:
                for i in range(3):
                    direction = random.randint(1, 4)
                    if direction == 1 and dwarf_y + 1 != WORLD_HEIGHT \
                            and grid[dwarf_y + 1][dwarf_x] in ALLOWED_TO_STEP_ON:
                        dwarf_y += 1
                    elif direction == 2 and dwarf_y - 1 != -1 \
                            and grid[dwarf_y - 1][dwarf_x] in ALLOWED_TO_STEP_ON:
                        dwarf_y -= 1
                    elif direction == 3 and dwarf_x + 1 != WORLD_WIDTH \
                            and grid[dwarf_y][dwarf_x + 1] in ALLOWED_TO_STEP_ON:
                        dwarf_x += 1
                    elif direction == 4 and dwarf_x - 1 != - 1 \
                            and grid[dwarf_y][dwarf_x - 1] in ALLOWED_TO_STEP_ON:
                        dwarf_x -= 1
        dwarf['dwarf_y'] = dwarf_y
        dwarf['dwarf_x'] = dwarf_x
        """when dwarf reaches goal it magically would eat its tenant 
        simply because for dwarf as it arrives at goal original_tenant the cursor is the only visible tenant
        if you remember we saved goal's original_tenant in goal dict
        now we feed it to dwarf as it will be the last one leaving this location
        so
        next for dwarf not to disappear we feed cursor with dwarf as original tenant so it is nicely stacked
        dwarf remembers what is under it and cursor remembers that there is also a dwarf in between"""
        if dwarf['dwarf_y'] == goal['goal_y'] and dwarf['dwarf_x'] == goal['goal_x']:
            dwarf['original_tenant'] = goal['goal_original_tenant']
            if goal['goal'] != 'eat' and goal_y == cursor['cursor_y'] and goal_x == cursor['cursor_x']:
                # without this dwarf would disappear - cursor stores info about what is below it
                # except tha case when user is not pointing at target - naturally cursor is not involved
                # IDK if both conditions are necessary
                cursor['original_tenant'] = 'A'
        else:
            dwarf['original_tenant'] = grid[dwarf_y][dwarf_x]
        grid[dwarf_y][dwarf_x] = 'A'
        clear_console()
        display_grid(grid)
        for i in range(7):
            print()
        time.sleep(speed)
        key = ''
        key = c.get_last_key_press()
        if key == 'r':
            return


def main():
    c = Canvas(600,100)
    c.create_rectangle(0, 0, 600, 100, "black")
    text = c.create_text(600// 2, 100 // 2, text='Click here to focus, then use keyboard', anchor='center', font_size=30, color='white')
    clear_console()
    greeting_screen(c)
    clear_console()
    # load world
    grid = create_grid()
    generate_mountain(grid)
    generate_trees(grid, 45)
    # load creatures
    dwarf = add_dwarf(grid)
    # with:
    # stats - has hp and hunger
    # EQ - has 0 of everything
    # load items
    food = add_food(grid, dwarf, 420)
    bed = {'bed_y': 0, 'bed_x': 0}
    # default sleeping spot
    cursor = add_cursor(grid)
    print("loading...")  # can be useful for testing
    print("Zoom out (Ctrl + -) so page doesnt scroll when using arrows")
    print()
    time.sleep(1)
    print("Build bed before night!")
    print()
    time.sleep(1)
    print("press enter")
    key = ''
    while key != 'Enter':
        key = c.get_last_key_press()
    time_of_the_day = 6.0
    is_it_night_or_day = 'day'
    speed = HEARTBEAT3
    what_speed = 'fast'
    # go
    clear_console()
    display_grid(grid)
    time.sleep(speed)
    while True:
        if time_of_the_day >= 24:
            time_of_the_day = 0
        # dwarf hunger option
        dwarf['dwarf_fullness'] -= 0.1  # for balanced gameplay 0.1
        key = ''
        input_from_canvas = c.get_last_key_press()
        if input_from_canvas == 'ArrowLeft':
            key = 'left'
        elif input_from_canvas == 'ArrowRight':
            key = 'right'
        elif input_from_canvas == 'ArrowUp':
            key = 'up'
        elif input_from_canvas == 'ArrowDown':
            key = 'down'
        elif input_from_canvas == 'm':
            key = 'm'  # like mine
        elif input_from_canvas == 'c':
            key = 'c'  # not like craft you silly, like chop wood
        elif input_from_canvas == 'b':
            key = 'b'  # like build
        elif input_from_canvas == 'g':
            key = 'g'  # like go
        elif input_from_canvas == '1':
            speed = HEARTBEAT1  # slow
            what_speed = 'slow'
        elif input_from_canvas == '2':
            speed = HEARTBEAT2  # normal
            what_speed = 'normal'
        elif input_from_canvas == '3':
            # noinspection SpellCheckingInspection
           speed = HEARTBEAT3  # fast boiiii
           what_speed = 'fast'
        elif input_from_canvas== 'q':
           # noinspection SpellCheckingInspection
           break  # like urwał mi od internetu
        move_cursor(cursor, grid, key)
        goal = create_goal(cursor, key, food, bed, is_it_night_or_day)
        if goal == 'none' and dwarf['dwarf_fullness'] < 50:
            goal = create_goal(cursor, 'hungry', food, bed, is_it_night_or_day)
            # first parameter does nothing here as goal is food not cursor position,
            # second is forced 'key' variable, third gives food coordinates
            if cursor['cursor_y'] == dwarf['dwarf_y'] and cursor['cursor_x'] == dwarf['dwarf_x']:
                cursor['original_tenant'] = dwarf['original_tenant']
            # this line ensures that dwarf isn't cloned
            # buggy behaviour originates from mechanism that
            # stores dwarf "graphics" in cursor when he gets to destination
            # normally before new goal is set user must move cursor to a new target
            # here target is set externally so cursor storing info is a bug because
            # as soon as dwarf reaches food and user moves cursor
            # the cursor outputs its original tenant hence clones dwarf (dwarf is on the food now)
            # even funnier when dwarf travels from bed to food it would clone bed and the other way around
        if goal == 'none' and is_it_night_or_day == 'night':
            goal = create_goal(cursor, 'sleepy', food, bed, is_it_night_or_day)
            if cursor['cursor_y'] == dwarf['dwarf_y'] and cursor['cursor_x'] == dwarf['dwarf_x']:
                cursor['original_tenant'] = dwarf['original_tenant']
        if goal != 'none':
            action_of_dwarf(dwarf, grid, cursor, goal, food, speed, bed, c)
        clear_console()
        display_grid(grid)
        # Debugging time!
        # print('dwarf', dwarf, 'cursor', cursor, 'goal', goal)
        # vitals bar
        print()
        print("time:", int(time_of_the_day), "it is", is_it_night_or_day, "| HP:", dwarf['dwarf_hp'],
              "| stomach fullness:", int(dwarf['dwarf_fullness']), "| game speed:", what_speed)
        # EQ bar
        print("Equipment:", "wood:", dwarf['dwarf_equipment']['wood'],
              "| rock chunks:", dwarf['dwarf_equipment']['rock_chunks'],
              "| food:", dwarf['dwarf_equipment']['food'])
        # controls
        print("arrows - move cursor, c - chop tree ♠, m - mine rock ■, b - build wooden wall ░ or bed B, g - go fo a walk, r - rescue if stuck, q - quit")
        # logic for displaying info about current position od cursor
        thing = ''
        if cursor['original_tenant'] == '♠':
            thing = "green ♠"
        if cursor['original_tenant'] == 'A':
            thing = "nice dwarf A"
        if cursor['original_tenant'] == '■':
            thing = "rocky ■"
        if cursor['original_tenant'] == '░':
            thing = "wooden ░"
        if cursor['original_tenant'] == '♥':
            thing = "food in quantity: " + str(food[2])
        print("Currently pointing at:", thing)
        print()
        time.sleep(speed)
        time_of_the_day += 0.025
        if time_of_the_day >= 22 or time_of_the_day < 6:
            is_it_night_or_day = 'night'
        else:
            is_it_night_or_day = 'day'


if __name__ == '__main__':
    main()
