import pyglet
from pyglet.window import key
import random
import os
from uuid import uuid4

from managers.action_manager import ActionManager

from components.actors.simple_actor import *
from components.grid.grid import *
from components.observer import Observer
from managers.state.simulation_state import ObjectiveSimulationState
from simulation.encounter import Encounter
from managers.simulation_manager import SimulationStateManager
from managers.entity_manager import EntityManager
from simulation import Simulation



WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800

action_manager = ActionManager()
state_manager = None
entity_manager = EntityManager()

win = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, caption='Gurps')


key_map = {}


@win.event
def on_key_press(key, modifiers):
    key_map[key] = True


batch = pyglet.graphics.Batch()

actors = {}
actor_components = {}
simulation = Simulation()
top_level_components = []

observers = {}
human = None

# TODO: abstract this into a 'world manager' (maybe remove ID from grid to have abstract references to it)
grid = Grid(10, 10)

objective_grid_view = GridComponent((40, 40), 50, grid, actor_components, batch)
subjective_grid_view = None # TODO: should be managed and constructed elsewhere


# TODO; repalce this with a comprehensive entity manager. currently a stub for showing things
def init_encounter():

    # Create the encounter, state, and simulation
    global state_manager
    objective_state = ObjectiveSimulationState(grid)
    state_manager = SimulationStateManager(objective_state)
    encounter = Encounter(objective_state)
    simulation.encounters.append(encounter)
    simulation.active_encounter = encounter

    # TODO: abstract this into 'actor manager' which creates all parts of the actor
    #  (stats, component, behavior) linked by ID
    global human
    for i in range(5):
        if i != 0:
            color = (random.random()/2, random.random()/2, random.random()/2)
            actor = SimpleActor(uuid4())
        else:
            color = (1,1,1)
            actor = HumanActor(uuid4(), key_map)
            human = actor.id

        # Fill in the objective data for the actor.
        actor_component = ActorComponent(None, None, color)

        state_manager.register_entity(actor.id)
        entity_manager.register_entity(actor.id, actor)
        actor_components[actor.id] = actor_component
        grid.insert((random.randint(0,9), random.randint(0,9)), actor.id)

    # Create a single grid view for the observer
    subjective_state = state_manager.generate_subjective_state(actor_id)
    grid_view = GridComponent((40, 40), 50,
                                     subjective_state.grid, actor_components, batch)


    main_view =

    # # Create a view for each actor, and allocate the observer.
    # for actor_id, component in actor_components.items():
    #     subjective_state = state_manager.generate_subjective_state(actor_id)
    #     grid_view = GridComponent((40, 40), 50,
    #                                      subjective_state.grid, actor_components, batch)
    #     observer = Observer(actor_id, grid_view)
    #     if actor_id == human:
    #         observer.active = True
    #
    #     observers[actor_id] = observer

    # Advance the turn by one to initialize it for the first player.
    encounter.advance_turn()


@win.event
def on_draw():
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(1, 1, 1)

    for comp in top_level_components:
        comp.draw()

    active_observers = list(filter(lambda observer: observer.active, observers.values()))
    if len(active_observers) > 1:
        raise Exception("Too many observers at one time.")

    for active_observer in active_observers:
        active_observer.view.draw()

    # # Render
    # for actor_id, actor_component in actor_components.items():
    #     actor_component.draw()

    #
    # for (x, y) in ((0, ARENA_HEIGHT),  # Top
    #                (-ARENA_WIDTH, 0),  # Left
    #                (0, 0),  # Center
    #                (ARENA_WIDTH, 0),  # Right
    #                (0, -ARENA_HEIGHT)):  # Bottom
    #     glLoadIdentity()
    #     glTranslatef(x, y, 0)
    #     wrapping_batch.draw()
    #
    # glLoadIdentity()
    # batch.draw()
    #
    # glLoadIdentity()
    #
    # if in_game:
    #     # HUD ship lives
    #     x = 10 + player.image.width // 2
    #     for i in range(player_lives - 1):
    #         player.image.blit(x, win.height - player.image.height // 2 - 10, 0)
    #         x += player.image.width + 10
    #
    #     # HUD score
    #     score_text.text = str(score)
    #     score_text.draw()
    #
    # if overlay:
    #     overlay.draw()
    #
    # if show_fps:
    #     fps_display.draw()


def update(dt):
    current_actor = simulation.active_encounter.current_actor_id
    current_subjective_state = simulation.active_encounter.current_simulation_state
    actions = actors[current_actor].update(current_subjective_state)
    if actions is not None:
        for action in actions:
            # Fake movement resolution
            current_loc = grid.get_loc(current_actor)
            next_loc = None

            if action == 1:
                next_loc = (current_loc[0], current_loc[1] + 1)
                grid.remove(current_actor)
            elif action == 2:
                next_loc = (current_loc[0], current_loc[1] - 1)
                grid.remove(current_actor)
            elif action == 3:
                next_loc = (current_loc[0] + 1, current_loc[1])
                grid.remove(current_actor)
            elif action == 4:
                next_loc = (current_loc[0] - 1, current_loc[1])
                grid.remove(current_actor)
            elif action == -1:
                # Advance the turn and update the state for a transition.
                simulation.active_encounter.advance_turn()
                current_actor = simulation.active_encounter.current_actor_id
                current_subjective_state = simulation.active_encounter.current_simulation_state

            if next_loc is not None:
                if next_loc[0] >= grid.x_size or next_loc[1] >= grid.y_size or next_loc[0] < 0 or next_loc[1] < 0:
                    next_loc = current_loc

                grid.insert(next_loc, current_actor)

        current_observer = observers[current_actor]

        if current_observer.active:
            current_observer.view.grid_data =
            subjective_grid_view.grid_data = current_subjective_state.grid
            subjective_grid_view.update_children()
    #
    # actions = action_manager.get_submitted_actions()
    # for action in actions:
    #     """TODO: Resolve Action"""

    # TODO:  Advance turn state
    # check if turn is over for active entity
    # if so advance active entity to next in the list.



    ''''''


init_encounter()
pyglet.clock.schedule_interval(update, 1/60.)
pyglet.app.run()
